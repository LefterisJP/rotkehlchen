import logging
from collections import defaultdict
from datetime import datetime, time
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    Set,
)

from eth_utils import to_checksum_address
from eth_utils.typing import HexAddress, HexStr

from rotkehlchen.accounting.structures import Balance
from rotkehlchen.assets.asset import EthereumToken
from rotkehlchen.assets.unknown_asset import UnknownEthereumToken
from rotkehlchen.assets.utils import get_ethereum_token
from rotkehlchen.chain.ethereum.graph import (
    format_query_indentation,
    Graph,
)
from rotkehlchen.constants import ZERO
from rotkehlchen.errors import RemoteError
from rotkehlchen.fval import FVal
from rotkehlchen.inquirer import Inquirer
from rotkehlchen.premium.premium import Premium
from rotkehlchen.typing import ChecksumEthAddress, Price
from rotkehlchen.user_messages import MessagesAggregator
from rotkehlchen.utils.interfaces import EthereumModule
from .graph import (
    LIQUIDITY_POSITIONS_QUERY,
    TOKEN_DAY_DATAS_QUERY,
)
from .typing import (
    AddressBalances,
    AssetPrice,
    DDAddressBalances,
    LiquidityPool,
    LiquidityPoolAsset,
    ProtocolBalance,
    uniswap_v2_lp_token,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.ethereum.manager import EthereumManager
    from rotkehlchen.db.dbhandler import DBHandler

log = logging.getLogger(__name__)


class Uniswap(EthereumModule):
    """Uniswap integration module

    * Uniswap subgraph:
    https://github.com/Uniswap/uniswap-v2-subgraph
    """
    def __init__(
            self,
            ethereum_manager: 'EthereumManager',
            database: 'DBHandler',
            premium: Optional[Premium],
            msg_aggregator: MessagesAggregator,
    ) -> None:
        self.ethereum = ethereum_manager
        self.database = database
        self.premium = premium
        self.msg_aggregator = msg_aggregator
        try:
            self.graph: Optional[Graph] = Graph(
                'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2',
            )
        except RemoteError as e:
            self.graph = None
            self.msg_aggregator.add_error(
                f'Could not initialize the Uniswap subgraph due to {str(e)}. '
                f'All uniswap historical queries are not functioning until this is fixed. '
                f'Probably will get fixed with time. If not report it to Rotkis support channel ',
            )

    def _convert_addresses_to_lower_case(
        self,
        addresses: List[ChecksumEthAddress],
    ) -> List[HexAddress]:
        return [HexAddress(HexStr(address.lower())) for address in addresses]

    def _get_balances_graph(
        self,
        addresses: List[ChecksumEthAddress],
    ) -> ProtocolBalance:
        """Get the addresses' pools data querying the Uniswap subgraph
        """
        addresses_lower = self._convert_addresses_to_lower_case(addresses)

        querystr = format_query_indentation(LIQUIDITY_POSITIONS_QUERY.format())
        limit = 1000
        param_types = {
            '$limit': 'Int!',
            '$offset': 'Int!',
            '$addresses': '[String!]',
            '$balance': 'BigDecimal!',
        }
        param_values = {
            'limit': limit,
            'offset': 0,
            'addresses': addresses_lower,
            'balance': "0",
        }

        address_balances: DDAddressBalances = defaultdict(list)
        known_assets: Set[EthereumToken] = set()
        unknown_assets: Set[UnknownEthereumToken] = set()

        while True:
            result = self.graph.query(  # type: ignore
                querystr=querystr,
                param_types=param_types,
                param_values=param_values,
            )
            result_data = result['liquidityPositions']

            if not result_data:
                break

            for lp in result_data:
                user_address = to_checksum_address(lp['user']['id'])
                user_lp_balance = FVal(lp['liquidityTokenBalance'])
                lp_pair = lp['pair']
                lp_address = to_checksum_address(lp_pair['id'])
                lp_total_supply = FVal(lp_pair['totalSupply'])

                # Insert LP tokens reserves within tokens dicts
                token0 = lp_pair['token0']
                token0['balance'] = lp_pair['reserve0']
                token1 = lp_pair['token1']
                token1['balance'] = lp_pair['reserve1']

                liquidity_pool_assets = []

                for token in token0, token1:
                    # Get the token <EthereumToken> or <UnknownEthereumToken>
                    asset = get_ethereum_token(
                        symbol=token['symbol'],
                        ethereum_address=to_checksum_address(token['id']),
                        name=token['name'],
                        decimals=int(token['decimals']),
                    )

                    # Classify the asset either as known or unknown
                    if isinstance(asset, EthereumToken):
                        known_assets.add(asset)
                    elif isinstance(asset, UnknownEthereumToken):
                        log.error(
                            f'Encountered unknown asset {asset.identifier} with '
                            f'address {asset.ethereum_address} in Uniswap. '
                            f'Instantiating UnknownEthereumToken',
                        )
                        unknown_assets.add(asset)

                    # Estimate the underlying asset balance
                    asset_balance = FVal(token['balance'])
                    user_asset_balance = (
                        user_lp_balance / lp_total_supply * asset_balance
                    )

                    liquidity_pool_asset = LiquidityPoolAsset(
                        asset=asset,
                        balance=asset_balance,
                        user_balance=Balance(amount=user_asset_balance),
                    )
                    liquidity_pool_assets.append(liquidity_pool_asset)

                # LP Uniswap V2 asset
                lp_uniswap_v2_asset = UnknownEthereumToken(
                    identifier=uniswap_v2_lp_token.symbol,
                    ethereum_address=lp_address,
                    name=uniswap_v2_lp_token.name,
                    decimals=uniswap_v2_lp_token.decimals,
                )
                liquidity_pool = LiquidityPool(
                    asset=lp_uniswap_v2_asset,
                    assets=liquidity_pool_assets,
                    total_supply=lp_total_supply,
                    user_balance=Balance(amount=user_lp_balance),
                )
                address_balances[user_address].append(liquidity_pool)

            # Update pagination step
            param_values['offset'] += limit  # type: ignore

        protocol_balance = ProtocolBalance(
            address_balances=dict(address_balances),
            known_assets=known_assets,
            unknown_assets=unknown_assets,
        )
        return protocol_balance

    def _get_balances_zerion(
        self,
        addresses: List[ChecksumEthAddress],
    ) -> ProtocolBalance:
        """Get the addresses' pools data via Zerion SDK.
        """
        address_balances: DDAddressBalances = defaultdict(list)
        known_assets: Set[EthereumToken] = set()
        unknown_assets: Set[UnknownEthereumToken] = set()

        protocol_balance = ProtocolBalance(
            address_balances=dict(address_balances),
            known_assets=known_assets,
            unknown_assets=unknown_assets,
        )
        return protocol_balance

    def _get_known_asset_price(
        self,
        known_assets: Set[EthereumToken],
        unknown_assets: Set[UnknownEthereumToken],
    ) -> AssetPrice:
        """Get the tokens prices via Inquirer

        Given an asset, if `find_usd_price()` returns zero, it will be added
        into `unknown_assets`.
        """
        asset_price: AssetPrice = {}

        for known_asset in known_assets:
            asset_usd_price = Inquirer().find_usd_price(known_asset)

            if asset_usd_price != Price(ZERO):
                asset_price[known_asset.ethereum_address] = FVal(asset_usd_price)
            else:
                unknown_asset = UnknownEthereumToken(
                    identifier=known_asset.identifier,
                    ethereum_address=known_asset.ethereum_address,
                    name=known_asset.name,
                    decimals=known_asset.decimals,
                )
                unknown_assets.add(unknown_asset)

        return asset_price

    def _get_unknown_asset_price_graph(
            self,
            unknown_assets: Set[UnknownEthereumToken],
    ) -> AssetPrice:
        """Get today's tokens prices via the Uniswap subgraph

        Uniswap provides a token price every day at 00:00:00 UTC
        """
        asset_price: AssetPrice = {}

        unknown_assets_addresses = [asset.ethereum_address for asset in unknown_assets]
        unknown_assets_addresses_lower = (
            self._convert_addresses_to_lower_case(unknown_assets_addresses)
        )

        querystr = format_query_indentation(TOKEN_DAY_DATAS_QUERY.format())
        limit = 1000
        today_epoch = int(datetime.combine(datetime.today(), time.min).timestamp())
        param_types = {
            '$limit': 'Int!',
            '$offset': 'Int!',
            '$token_ids': '[String!]',
            '$datetime': 'Int!',
        }
        param_values = {
            'limit': limit,
            'offset': 0,
            'token_ids': unknown_assets_addresses_lower,
            'datetime': today_epoch,
        }
        while True:
            result = self.graph.query(  # type: ignore
                querystr=querystr,
                param_types=param_types,
                param_values=param_values,
            )
            result_data = result['tokenDayDatas']

            if not result_data:
                break

            for tdd in result_data:
                asset_price[to_checksum_address(tdd['token']['id'])] = FVal(tdd['priceUSD'])

            # Update pagination step
            param_values['offset'] += limit  # type: ignore

        return asset_price

    def _update_assets_prices_in_address_balances(
            self,
            address_balances: AddressBalances,
            known_asset_price: AssetPrice,
            unknown_asset_price: AssetPrice,
    ) -> None:
        """Update the pools underlying assets prices in USD (prices obtained
        via Inquirer and the Uniswap subgraph)
        """
        for lps in address_balances.values():
            for lp in lps:
                # Try to get price from either known or unknown asset price.
                # Otherwise keep existing price (zero)
                total_user_balance = FVal(0)
                for asset in lp.assets:
                    asset_ethereum_address = asset.asset.ethereum_address
                    asset_usd = known_asset_price.get(
                        asset_ethereum_address,
                        unknown_asset_price.get(asset_ethereum_address, ZERO),
                    )
                    # Update <LiquidityPoolAsset> if asset USD price exists
                    if asset_usd != ZERO:
                        asset.asset_usd = Price(asset_usd)
                        asset.user_balance.usd_value = (
                            asset.user_balance.amount * asset_usd
                        )

                    total_user_balance += asset.user_balance.usd_value

                # Update <LiquidityPool> total balance in USD
                lp.user_balance.usd_value = total_user_balance

    def get_balances(
        self,
        addresses: List[ChecksumEthAddress],
        graph_query: bool,
    ) -> AddressBalances:
        """Get the addresses' balances in the Uniswap protocol

        Premium users can request balances either via the Uniswap subgraph or
        Zerion SDK.
        """
        is_graph_mode = self.graph and self.premium and graph_query

        if is_graph_mode:
            protocol_balance = self._get_balances_graph(addresses)
        else:
            protocol_balance = self._get_balances_zerion(addresses)

        known_assets = protocol_balance.known_assets
        unknown_assets = protocol_balance.unknown_assets

        known_asset_price = self._get_known_asset_price(known_assets, unknown_assets)

        unknown_asset_price: AssetPrice = {}
        if is_graph_mode:
            unknown_asset_price = self._get_unknown_asset_price_graph(unknown_assets)

        self._update_assets_prices_in_address_balances(
            protocol_balance.address_balances,
            known_asset_price,
            unknown_asset_price,
        )

        return protocol_balance.address_balances

    # -- Methods following the EthereumModule interface -- #
    def on_startup(self) -> None:
        pass

    def on_account_addition(self, address: ChecksumEthAddress) -> None:
        pass

    def on_account_removal(self, address: ChecksumEthAddress) -> None:
        pass
