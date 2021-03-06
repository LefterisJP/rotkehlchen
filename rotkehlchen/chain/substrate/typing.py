from enum import Enum
from typing import Dict, List, NamedTuple, NewType, Tuple, Type, Union

from substrateinterface import SubstrateInterface

KusamaAddress = NewType('KusamaAddress', str)
SubstrateAddress = Union[KusamaAddress]

SubstrateChainId = NewType('SubstrateChainId', str)
BlockNumber = NewType('BlockNumber', int)


class KusamaNodeName(Enum):
    """Public nodes for Kusama.
    """
    OWN = 0
    PARITY = 1

    def __str__(self) -> str:
        if self == KusamaNodeName.OWN:
            return 'own node'
        if self == KusamaNodeName.PARITY:
            return 'parity'
        raise AssertionError(f'Unexpected KusamaNodeName: {self}')

    def endpoint(self) -> str:
        if self == KusamaNodeName.OWN:
            raise NotImplementedError(
                'The endpoint url for a substrate own node must be got either '
                'via "own_rpc_endpoint" or the specific db setting',
            )
        if self == KusamaNodeName.PARITY:
            return 'https://kusama-rpc.polkadot.io/'
        raise AssertionError(f'Unexpected KusamaNodeName: {self}')


NodeName = Union[KusamaNodeName]


class SubstrateInterfaceAttributes(NamedTuple):
    type_registry_preset: str


class SubstrateChain(Enum):
    """Supported Substrate chains.
    """
    KUSAMA = 1

    def __str__(self) -> SubstrateChainId:
        """Return the official chain identifier/name.
        """
        if self == SubstrateChain.KUSAMA:
            return SubstrateChainId('Kusama')
        raise AssertionError(f'Unexpected Chain: {self}')

    def chain_explorer_api(self) -> str:
        """Return the explorer API.

        NB: this simplified implementation relies on Subscan API supporting all
        the chains we introduce.
        """
        if self == SubstrateChain.KUSAMA:
            return 'https://kusama.subscan.io/api'
        raise AssertionError(f'Unexpected Chain: {self}')

    def substrate_interface_attributes(self) -> SubstrateInterfaceAttributes:
        """Return the attributes for instantiating SubstrateInterface.
        """
        if self == SubstrateChain.KUSAMA:
            return SubstrateInterfaceAttributes(type_registry_preset='kusama')
        raise AssertionError(f'Unexpected Chain: {self}')

    def blocks_threshold(self) -> BlockNumber:
        """Return the blocks difference that marks a node as unsynced.
        """
        if self == SubstrateChain.KUSAMA:
            return BlockNumber(10)
        raise AssertionError(f'Unexpected Chain: {self}')

    def node_name_type(self) -> Union[Type[KusamaNodeName]]:
        """Return the NodeName enum.
        """
        if self == SubstrateChain.KUSAMA:
            return KusamaNodeName
        raise AssertionError(f'Unexpected Chain: {self}')


class NodeNameAttributes(NamedTuple):
    node_interface: SubstrateInterface
    weight_block: BlockNumber


DictNodeNameNodeAttributes = Dict[NodeName, NodeNameAttributes]
NodesCallOrder = List[Tuple[NodeName, NodeNameAttributes]]
