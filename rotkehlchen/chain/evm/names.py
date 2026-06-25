import logging
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

from rotkehlchen.chain.ethereum.decoding.constants import (
    KRAKEN_ADDRESSES,
    POLONIEX_ADDRESS,
    UPHOLD_ADDRESS,
)
from rotkehlchen.constants import ENS_UPDATE_INTERVAL
from rotkehlchen.db.addressbook import DBAddressbook
from rotkehlchen.db.dbhandler import DBHandler
from rotkehlchen.db.ens import DBEns
from rotkehlchen.db.settings import CachedSettings
from rotkehlchen.errors.misc import BlockchainQueryError, InputError, RemoteError
from rotkehlchen.globaldb.handler import GlobalDBHandler
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.types import (
    AddressbookEntryWithSource,
    AddressbookType,
    AddressNameSource,
    ChainID,
    ChecksumEvmAddress,
    EnsMapping,
    OptionalChainAddress,
    SupportedBlockchain,
    Timestamp,
)
from rotkehlchen.utils.misc import ts_now

if TYPE_CHECKING:
    from rotkehlchen.chain.ethereum.node_inquirer import EthereumInquirer

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def find_ens_mappings(
        ethereum_inquirer: 'EthereumInquirer',
        addresses: list[ChecksumEvmAddress],
        ignore_cache: bool,
) -> dict[ChecksumEvmAddress, str]:
    """
    Find and return ens names for the given addresses.
    First check the db, and if can't find, call the blockchain.

    IMPORTANT: If this implementation changes also change the one in tests/api/test_ens.py

    May raise:
    - RemoteError if was not able to query blockchain
    """
    dbens = DBEns(ethereum_inquirer.database)
    ens_mappings: dict[ChecksumEvmAddress, str] = {}
    if ignore_cache:
        addresses_to_query = addresses
    else:
        addresses_to_query = []
        with dbens.db.conn.read_ctx() as cursor:
            cached_data = dbens.get_reverse_ens(cursor=cursor, addresses=addresses)
        cur_time = ts_now()
        for address, cached_value in cached_data.items():
            has_name = isinstance(cached_value, EnsMapping)
            last_update: Timestamp = cached_value.last_update if has_name else cached_value  # type: ignore  # mypy doesn't see `isinstance` check
            if cur_time - last_update > ENS_UPDATE_INTERVAL:
                addresses_to_query.append(address)
            elif has_name:
                ens_mappings[cached_value.address] = cached_value.name  # type: ignore
        addresses_to_query += list(set(addresses) - set(cached_data.keys()))

    try:
        query_results = ethereum_inquirer.ens_reverse_lookup(addresses_to_query)
    except (RemoteError, BlockchainQueryError) as e:
        raise RemoteError(f'Error occurred while querying ens names: {e!s}') from e

    with dbens.db.user_write() as write_cursor:
        return dbens.update_values(
            write_cursor=write_cursor,
            ens_lookup_results=query_results,
            mappings_to_send=ens_mappings,
        )


def search_for_addresses_names(
        prioritizer: 'NamePrioritizer',
        chain_addresses: list[OptionalChainAddress],
) -> list[AddressbookEntryWithSource]:
    """
    This method searches for all names of provided addresses known to rotki. We can show
    only one name per address, and thus we prioritize known names. Priority is read from settings.

    For now this works only for evm chains.
    TODO: support not only ChecksumEvmAddress, but other address formats too.
    """
    return prioritizer.get_prioritized_names(
        prioritized_name_source=CachedSettings().get_entry('address_name_priority'),  # type: ignore  # mypy doesn't detect correctly the type of the cached setting
        chain_addresses=chain_addresses,
    )


def maybe_resolve_name(
        ethereum_inquirer: 'EthereumInquirer',
        name: str,
        ignore_cache: bool,
) -> ChecksumEvmAddress | None:
    """Resolve name by either checking the DB or asking the chain"""
    dbens = DBEns(ethereum_inquirer.database)
    if not ignore_cache:
        with dbens.db.conn.read_ctx() as cursor:
            if (resolved_name := dbens.get_address_for_name(
                cursor=cursor,
                name=name,
            )) is not None:
                return resolved_name

    try:
        resolved_address = ethereum_inquirer.ens_lookup(name)
    except (RemoteError, InputError) as e:
        log.debug(f'Could not resolve ENS {name} to an address due to {e}')
        resolved_address = None

    if resolved_address is None:
        return None

    with dbens.db.user_write() as write_cursor:
        dbens.update_values(  # update cache if needed
            write_cursor=write_cursor,
            ens_lookup_results={resolved_address: name},
            mappings_to_send={},
        )
    return resolved_address


# A fetcher resolves a single name source for many addresses at once, returning a mapping of
# chain_address -> name for those addresses that have a name from that source.
FetcherFunc = Callable[[DBHandler, list[OptionalChainAddress]], dict[OptionalChainAddress, str]]


class NamePrioritizer:
    def __init__(self, database: DBHandler):
        self._fetchers: dict[AddressNameSource, FetcherFunc] = {}
        self._db = database
        self.add_fetchers({
            'blockchain_account': _blockchain_addresses_to_names,
            'global_addressbook': _global_addressbook_addresses_to_names,
            'private_addressbook': _private_addressbook_addresses_to_names,
            'ethereum_tokens': _token_mappings_addresses_to_names,
            'hardcoded_mappings': _hardcoded_addresses_to_names,
            'ens_names': _ens_addresses_to_names,
        })

    def add_fetchers(self, fetchers: dict[AddressNameSource, FetcherFunc]) -> None:
        self._fetchers.update(fetchers)

    def get_prioritized_names(
            self,
            prioritized_name_source: Sequence[AddressNameSource],
            chain_addresses: list[OptionalChainAddress],
    ) -> list[AddressbookEntryWithSource]:
        """
        Gets the name from the name source with the highest priority.
        Name source ids with lower index have a higher priority.

        Each source is resolved for all still-unnamed addresses in a single batch (instead of one
        query per address per source) and prioritized in memory. Sources are tried in priority
        order and an address drops out of the remaining set as soon as a name is found for it.
        """
        resolved: dict[OptionalChainAddress, tuple[str, AddressNameSource]] = {}
        remaining = list(dict.fromkeys(chain_addresses))  # unique, order-preserving
        for name_source in prioritized_name_source:
            if len(remaining) == 0:
                break

            fetcher = self._fetchers.get(name_source)
            if not fetcher:
                raise NotImplementedError(
                    f'address name fetcher for "{name_source}" is not implemented',
                )

            names = fetcher(self._db, remaining)
            next_remaining = []
            for chain_address in remaining:
                if (name := names.get(chain_address)) is not None:
                    resolved[chain_address] = name, name_source
                else:
                    next_remaining.append(chain_address)
            remaining = next_remaining

        return [
            AddressbookEntryWithSource(
                name=resolved[chain_address][0],
                address=chain_address.address,
                blockchain=chain_address.blockchain,
                source=resolved[chain_address][1],
            )
            for chain_address in chain_addresses if chain_address in resolved
        ]


def _blockchain_addresses_to_names(
        db: DBHandler,
        chain_addresses: list[OptionalChainAddress],
) -> dict[OptionalChainAddress, str]:
    """Returns the labels of evm blockchain accounts (stored in the private addressbook).
    Only pairs that specify a blockchain are considered.
    """
    if len(with_blockchain := [
        chain_address for chain_address in chain_addresses if chain_address.blockchain is not None
    ]) == 0:
        return {}

    return DBAddressbook(db).get_addressbook_entry_names(
        book_type=AddressbookType.PRIVATE,
        chain_addresses=with_blockchain,
    )


def _private_addressbook_addresses_to_names(
        db: DBHandler,
        chain_addresses: list[OptionalChainAddress],
) -> dict[OptionalChainAddress, str]:
    """Returns the names of private addressbook entries for the given addresses."""
    return DBAddressbook(db).get_addressbook_entry_names(
        book_type=AddressbookType.PRIVATE,
        chain_addresses=chain_addresses,
    )


def _global_addressbook_addresses_to_names(
        db: DBHandler,
        chain_addresses: list[OptionalChainAddress],
) -> dict[OptionalChainAddress, str]:
    """Returns the names of global addressbook entries for the given addresses."""
    return DBAddressbook(db).get_addressbook_entry_names(
        book_type=AddressbookType.GLOBAL,
        chain_addresses=chain_addresses,
    )


def _hardcoded_addresses_to_names(
        _: DBHandler,
        chain_addresses: list[OptionalChainAddress],
) -> dict[OptionalChainAddress, str]:
    """Returns the names of known hardcoded addresses (in-memory, no query)."""
    names: dict[OptionalChainAddress, str] = {}
    for chain_address in chain_addresses:
        if chain_address.blockchain != SupportedBlockchain.ETHEREUM:
            continue

        if chain_address.address in KRAKEN_ADDRESSES:
            names[chain_address] = 'Kraken'
        elif chain_address.address == POLONIEX_ADDRESS:
            names[chain_address] = 'Poloniex'
        elif chain_address.address == UPHOLD_ADDRESS:
            names[chain_address] = 'Uphold.com'

    return names


def _token_mappings_addresses_to_names(
        _: DBHandler,
        chain_addresses: list[OptionalChainAddress],
) -> dict[OptionalChainAddress, str]:
    """Returns the token names for the evm token address/chain id combinations in the global DB."""
    requested: dict[OptionalChainAddress, tuple[ChecksumEvmAddress, ChainID]] = {
        chain_address: (chain_address.address, chain_address.blockchain.to_chain_id())
        for chain_address in chain_addresses
        if chain_address.blockchain is not None and chain_address.blockchain.is_evm()
    }
    if len(requested) == 0:
        return {}

    token_names = GlobalDBHandler.get_token_names(list(requested.values()))
    return {
        chain_address: name
        for chain_address, token_key in requested.items()
        if (name := token_names.get(token_key)) is not None
    }


def _ens_addresses_to_names(
        db: DBHandler,
        chain_addresses: list[OptionalChainAddress],
) -> dict[OptionalChainAddress, str]:
    """Returns the ens names for the given addresses, read from the local cache in one query."""
    db_ens = DBEns(db)
    with db.conn.read_ctx() as cursor:
        reverse_ens = db_ens.get_reverse_ens(
            cursor=cursor,
            addresses=list({chain_address.address for chain_address in chain_addresses}),
        )

    names: dict[OptionalChainAddress, str] = {}
    for chain_address in chain_addresses:
        if isinstance(address_ens := reverse_ens.get(chain_address.address), EnsMapping):
            names[chain_address] = address_ens.name

    return names
