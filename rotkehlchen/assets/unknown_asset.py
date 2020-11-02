from dataclasses import dataclass, field
from typing import (
    Any,
    Optional,
)

from rotkehlchen.typing import ChecksumEthAddress


@dataclass(init=True, repr=True, eq=False, unsafe_hash=False, frozen=True)
class UnknownEthereumToken:
    """Alternative minimal class to EthereumToken for unknown assets"""
    identifier: str
    ethereum_address: ChecksumEthAddress
    name: Optional[str] = None
    decimals: Optional[int] = None
    symbol: str = field(init=False)

    def __post_init__(self) -> None:
        """Asset post initialization as the frozen property is desirable
        """
        object.__setattr__(self, 'symbol', self.identifier)

    def __hash__(self) -> int:
        return hash((self.identifier, self.ethereum_address))

    def __eq__(self, other: Any) -> bool:
        if other is None:
            return False
        if not isinstance(other, UnknownEthereumToken):
            raise TypeError(f'Invalid type: {type(other)}')

        return (
            self.identifier == other.identifier and
            self.ethereum_address == other.ethereum_address
        )

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return self.name or self.identifier

    def __repr__(self) -> str:
        return (
            f'<UnknownEthereumToken '
            f'identifier:{self.identifier} '
            f'ethereum_address:{self.ethereum_address} '
            f'name:{self.name} '
            f'symbol:{self.symbol} '
            f'decimals: {self.decimals}>'
        )

    def serialize(self) -> str:
        return self.identifier
