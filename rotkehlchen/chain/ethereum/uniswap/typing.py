from dataclasses import dataclass
from typing import (
    DefaultDict,
    Dict,
    List,
    NamedTuple,
    Set,
    Union,
)

from rotkehlchen.accounting.structures import Balance
from rotkehlchen.assets.asset import EthereumToken
from rotkehlchen.assets.unknown_asset import UnknownEthereumToken
from rotkehlchen.constants import ZERO
from rotkehlchen.fval import FVal
from rotkehlchen.typing import (
    ChecksumEthAddress,
    Price,
)


class UniswapV2LPToken(NamedTuple):
    name: str
    symbol: str
    decimals: int


uniswap_v2_lp_token = (
    UniswapV2LPToken(name='Uniswap V2', symbol='UNI-V2', decimals=18))


@dataclass(init=True, repr=True)
class LiquidityPoolAsset:
    asset: Union[EthereumToken, UnknownEthereumToken]
    balance: FVal
    user_balance: Balance
    asset_usd: Price = Price(ZERO)

    def serialize(self) -> Dict:
        return {
            'asset': self.asset.serialize(),
            'asset_usd': self.asset_usd,
            'balance': self.balance,
            'user_balance': self.user_balance.serialize(),
        }


@dataclass(init=True, repr=True)
class LiquidityPool:
    asset: UnknownEthereumToken
    assets: List[LiquidityPoolAsset]
    total_supply: FVal
    user_balance: Balance

    def serialize(self) -> Dict:
        return {
            'asset': self.asset.serialize(),
            'assets': [asset.serialize() for asset in self.assets],
            'total_supply': self.total_supply,
            'user_balance': self.user_balance.serialize(),
        }


AddressBalances = Dict[ChecksumEthAddress, List[LiquidityPool]]
DDAddressBalances = DefaultDict[ChecksumEthAddress, List[LiquidityPool]]
AssetPrice = Dict[ChecksumEthAddress, FVal]


class ProtocolBalance(NamedTuple):
    address_balances: AddressBalances
    known_assets: Set[EthereumToken]
    unknown_assets: Set[UnknownEthereumToken]
