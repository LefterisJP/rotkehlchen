from typing import TYPE_CHECKING, Literal

from rotkehlchen.chain.ethereum.airdrops import AIRDROP_IDENTIFIER_KEY
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType

if TYPE_CHECKING:
    from rotkehlchen.assets.asset import Asset
    from rotkehlchen.fval import FVal
    from rotkehlchen.history.events.structures.evm_event import EvmEvent
    from rotkehlchen.types import ChecksumEvmAddress


def match_airdrop_claim(
        event: 'EvmEvent',
        user_address: 'ChecksumEvmAddress',
        amount: 'FVal',
        asset: 'Asset',
        counterparty: str,
        airdrop_identifier: Literal['shapeshift', 'badger', 'cow_mainnet', 'cow_gnosis', 'convex', 'fpis', 'scroll', 'walletconnect'],  # noqa: E501
        notes: str | None = None,
) -> bool:
    """It matches a transfer event to an airdrop claim, changes the required fields
     then returns `True` if a match was found"""
    if not (event.event_type == HistoryEventType.RECEIVE and event.location_label == user_address and amount == event.amount and asset == event.asset):  # noqa: E501
        return False

    event.event_subtype = HistoryEventSubType.AIRDROP
    event.counterparty = counterparty
    event.notes = f'Claim {amount} {asset.symbol_or_name()} from {counterparty} airdrop' if notes is None else notes  # noqa: E501
    event.extra_data = {AIRDROP_IDENTIFIER_KEY: airdrop_identifier}
    return True
