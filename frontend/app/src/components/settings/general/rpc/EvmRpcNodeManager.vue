<script setup lang="ts">
import { camelCase } from 'es-toolkit';
import {
  type EvmRpcNode,
  type EvmRpcNodeList,
  type EvmRpcNodeManageState,
  getPlaceholderNode,
} from '@/types/settings/rpc';
import { useConfirmStore } from '@/store/confirm';
import { usePeriodicStore } from '@/store/session/periodic';
import { useMessageStore } from '@/store/message';
import { useNotificationsStore } from '@/store/notifications';
import { useEvmNodesApi } from '@/composables/api/settings/evm-nodes-api';
import { useSupportedChains } from '@/composables/info/chains';
import EvmRpcNodeFormDialog from '@/components/settings/general/rpc/EvmRpcNodeFormDialog.vue';
import RowActions from '@/components/helper/RowActions.vue';
import BadgeDisplay from '@/components/history/BadgeDisplay.vue';
import SimpleTable from '@/components/common/SimpleTable.vue';
import type { Blockchain } from '@rotki/common';

const props = defineProps<{
  chain: Blockchain;
}>();

const { t } = useI18n();

const { chain } = toRefs(props);

const nodes = ref<EvmRpcNodeList>([]);
const state = ref<EvmRpcNodeManageState>();
const reconnecting = ref<boolean>(false);

const { notify } = useNotificationsStore();
const { setMessage } = useMessageStore();

const { connectedNodes } = storeToRefs(usePeriodicStore());
const api = useEvmNodesApi(chain);
const { getChainName, getEvmChainName } = useSupportedChains();

const chainName = computed(() => get(getChainName(chain)));

async function loadNodes(): Promise<void> {
  try {
    set(nodes, await api.fetchEvmNodes());
  }
  catch (error: any) {
    notify({
      message: error.message,
      title: t('evm_rpc_node_manager.loading_error.title', {
        chain: get(chain),
      }),
    });
  }
}

function editRpcNode(node: EvmRpcNode) {
  set(state, {
    mode: 'edit',
    node,
  });
}

function addNewRpcNode() {
  set(state, {
    mode: 'add',
    node: getPlaceholderNode(get(chain)),
  });
}

async function deleteNode(node: EvmRpcNode) {
  try {
    const identifier = node.identifier;
    await api.deleteEvmNode(identifier);
    await loadNodes();
  }
  catch (error: any) {
    setMessage({
      description: error.message,
      success: false,
      title: t('evm_rpc_node_manager.delete_error.title', {
        chain: get(chain),
      }),
    });
  }
}

async function onActiveChange(active: boolean, node: EvmRpcNode) {
  const state = { ...node, active };
  try {
    await api.editEvmNode(state);
    await loadNodes();
  }
  catch (error: any) {
    setMessage({
      description: error.message,
      success: false,
      title: t('evm_rpc_node_manager.activate_error.title', {
        node: node.name,
      }),
    });
  }
}

function isEtherscan(item: EvmRpcNode) {
  return !item.endpoint && item.name.includes('etherscan');
}

function isNodeConnected(item: EvmRpcNode): boolean {
  const blockchain = get(chain);
  const connected = get(connectedNodes);
  const evmChain = camelCase(getEvmChainName(blockchain) ?? '');
  const nodes = evmChain && connected[evmChain] ? connected[evmChain] : [];

  return nodes.includes(item.name) || isEtherscan(item);
}

const { show } = useConfirmStore();

function showDeleteConfirmation(item: EvmRpcNode) {
  const chainProp = get(chainName);
  show(
    {
      message: t('evm_rpc_node_manager.confirm.message', {
        chain: chainProp,
        endpoint: item.endpoint,
        node: item.name,
      }),
      title: t('evm_rpc_node_manager.confirm.title', { chain: chainProp }),
    },
    () => deleteNode(item),
  );
}

const anyDisconnected = computed(() => get(nodes).some(node => !isNodeConnected(node) && node.active));

async function reConnect(identifier?: number) {
  set(reconnecting, true);
  const success = await api.reConnectNode(identifier);
  set(reconnecting, false);

  if (success) {
    await loadNodes();
  }
}

onMounted(async () => {
  await loadNodes();
});

defineExpose({
  addNewRpcNode,
});
</script>

<template>
  <SimpleTable class="bg-white dark:bg-transparent">
    <thead>
      <tr>
        <th>{{ t('evm_rpc_node_manager.node') }}</th>
        <th>{{ t('evm_rpc_node_manager.node_weight') }}</th>
        <th>
          <div class="flex items-center gap-2">
            <div class="w-6">
              <RuiTooltip
                v-if="anyDisconnected"
                :open-delay="400"
              >
                <template #activator>
                  <RuiButton
                    :disabled="reconnecting"
                    icon
                    color="primary"
                    variant="text"
                    size="sm"
                    @click="reConnect()"
                  >
                    <RuiIcon
                      name="lu-rotate-cw"
                      size="16"
                    />
                  </RuiButton>
                </template>
                {{ t('evm_rpc_node_manager.reconnect.all') }}
              </RuiTooltip>
            </div>
            {{ t('evm_rpc_node_manager.connectivity') }}
          </div>
        </th>
        <th />
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="(item, index) in nodes"
        :key="index + item.name"
        class="border-b border-default"
        data-cy="ethereum-node"
      >
        <td>
          <div class="flex gap-3 items-center">
            <RuiTooltip
              v-if="!item.owned"
              :popper="{ placement: 'top' }"
              :open-delay="400"
            >
              <template #activator>
                <RuiIcon
                  name="lu-earth"
                  class="text-rui-text-secondary"
                />
              </template>
              <span>{{ t('evm_rpc_node_manager.public_node') }}</span>
            </RuiTooltip>
            <RuiTooltip
              v-else
              :popper="{ placement: 'top' }"
              :open-delay="400"
            >
              <template #activator>
                <RuiIcon
                  name="lu-user"
                  class="text-rui-text-secondary"
                />
              </template>
              <span>{{ t('evm_rpc_node_manager.private_node') }}</span>
            </RuiTooltip>
            <div>
              <div class="font-medium">
                {{ item.name }}
              </div>
              <div class="text-rui-text-secondary text-sm">
                {{ !isEtherscan(item) ? item.endpoint : t('evm_rpc_node_manager.etherscan') }}
              </div>
            </div>
          </div>
        </td>
        <td>
          <span v-if="!item.owned">
            {{
              t('evm_rpc_node_manager.weight', {
                weight: item.weight,
              })
            }}
          </span>
        </td>
        <td>
          <div class="flex items-center gap-2">
            <div class="w-6">
              <RuiTooltip
                v-if="!isNodeConnected(item) && item.active"
                :open-delay="400"
              >
                <template #activator>
                  <RuiButton
                    :disabled="reconnecting"
                    icon
                    color="primary"
                    variant="text"
                    size="sm"
                    @click="reConnect(item.identifier)"
                  >
                    <RuiIcon
                      name="lu-rotate-cw"
                      size="16"
                    />
                  </RuiButton>
                </template>
                {{ t('evm_rpc_node_manager.reconnect.single') }}
              </RuiTooltip>
            </div>
            <BadgeDisplay
              v-if="isNodeConnected(item)"
              color="green"
              class="items-center gap-2 !leading-6"
            >
              <RuiIcon
                color="success"
                size="16"
                name="lu-wifi"
              />
              <span>
                {{ t('evm_rpc_node_manager.connected.true') }}
              </span>
            </BadgeDisplay>
            <BadgeDisplay
              v-else
              color="red"
              class="items-center gap-2 !leading-6"
            >
              <RuiIcon
                color="error"
                size="16"
                name="lu-wifi-off"
              />
              <span>
                {{ t('evm_rpc_node_manager.connected.false') }}
              </span>
            </BadgeDisplay>
          </div>
        </td>
        <td>
          <div class="flex items-center gap-2 justify-end">
            <RuiSwitch
              color="primary"
              hide-details
              class="mr-4"
              :model-value="item.active"
              :disabled="isEtherscan(item)"
              @update:model-value="onActiveChange($event, item)"
            />
            <RowActions
              :delete-tooltip="t('evm_rpc_node_manager.delete_tooltip')"
              :delete-disabled="isEtherscan(item)"
              :edit-tooltip="t('evm_rpc_node_manager.edit_tooltip')"
              @edit-click="editRpcNode(item)"
              @delete-click="showDeleteConfirmation(item)"
            />
          </div>
        </td>
      </tr>
    </tbody>
  </SimpleTable>
  <EvmRpcNodeFormDialog
    v-model="state"
    @complete="loadNodes()"
  />
</template>
