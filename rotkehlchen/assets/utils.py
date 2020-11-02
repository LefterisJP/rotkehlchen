from typing import Any, Optional, Union

from rotkehlchen.errors import UnknownAsset
from rotkehlchen.typing import ChecksumEthAddress

from .asset import EthereumToken
from .unknown_asset import UnknownEthereumToken


def get_ethereum_token(
        symbol: str,
        ethereum_address: ChecksumEthAddress,
        name: Optional[str] = None,
        decimals: Optional[int] = None,
) -> Union[EthereumToken, UnknownEthereumToken]:
    """Given a token symbol and address return the <EthereumToken>, otherwise
    an <UnknownEthereumToken>.
    """
    ethereum_token: Any = None
    is_unknown_asset = False
    try:
        ethereum_token = EthereumToken(symbol)
    except UnknownAsset:
        is_unknown_asset = True
    else:
        if ethereum_token.ethereum_address != ethereum_address:
            is_unknown_asset = True
    finally:
        if is_unknown_asset:
            ethereum_token = UnknownEthereumToken(
                identifier=symbol,
                ethereum_address=ethereum_address,
                name=name,
                decimals=decimals
            )

    return ethereum_token
