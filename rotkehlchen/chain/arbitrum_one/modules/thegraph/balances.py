from typing import TYPE_CHECKING

from rotkehlchen.chain.arbitrum_one.modules.thegraph.constants import CONTRACT_STAKING
from rotkehlchen.chain.ethereum.interfaces.balances import BalancesSheetType
from rotkehlchen.chain.evm.decoding.thegraph.balances import ThegraphCommonBalances
from rotkehlchen.constants.assets import A_GRT_ARB

if TYPE_CHECKING:
    from rotkehlchen.chain.arbitrum_one.decoding.decoder import ArbitrumOneTransactionDecoder
    from rotkehlchen.chain.arbitrum_one.node_inquirer import ArbitrumOneInquirer


class ThegraphBalances(ThegraphCommonBalances):

    def __init__(
            self,
            evm_inquirer: 'ArbitrumOneInquirer',
            tx_decoder: 'ArbitrumOneTransactionDecoder',
    ) -> None:
        super().__init__(
            evm_inquirer=evm_inquirer,
            tx_decoder=tx_decoder,
            native_asset=A_GRT_ARB,
            staking_contract=CONTRACT_STAKING,
        )

    def query_balances(self) -> BalancesSheetType:
        """Queries and returns the balances sheet for staking events.

        Retrieves deposit events and processes them to generate a unique set of delegations.
        Supports both simple and vested staking."""
        # On Arbitrum, we also want to process Ethereum HistoryEvents, cause of the access to
        # required extra_data (delegator_l2, indexer_l2) so we ask for all locations
        return self._base_balance_query(location=None)
