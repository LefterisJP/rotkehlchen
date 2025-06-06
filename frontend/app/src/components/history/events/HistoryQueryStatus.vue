<script setup lang="ts">
import { TaskType } from '@/types/task-type';
import { useTaskStore } from '@/store/tasks';
import { useHistoryStore } from '@/store/history';
import { useTransactionQueryStatus } from '@/composables/history/events/query-status/tx-query-status';
import { useEventsQueryStatus } from '@/composables/history/events/query-status/events-query-status';
import HistoryQueryStatusDialog from '@/components/history/events/HistoryQueryStatusDialog.vue';
import EventsDecodingStatusCurrent from '@/components/history/events/EventsDecodingStatusCurrent.vue';
import HistoryQueryStatusCurrent from '@/components/history/events/HistoryQueryStatusCurrent.vue';
import EventsCacheRefreshStatusCurrent from '@/components/history/events/EventsCacheRefreshStatusCurrent.vue';
import HistoryQueryStatusBar from '@/components/history/events/HistoryQueryStatusBar.vue';
import type { Blockchain } from '@rotki/common';
import type {
  EvmTransactionQueryData,
  HistoryEventsQueryData,
} from '@/types/websocket-messages';

const currentAction = defineModel<'decode' | 'query'>('currentAction', { required: true });

const props = withDefaults(defineProps<{
  colspan: number;
  loading: boolean;
  onlyChains?: Blockchain[];
  locations?: string[];
  decoding: boolean;
}>(), {
  loading: false,
  locations: () => [],
  onlyChains: () => [],
});

const emit = defineEmits<{
  'show:dialog': [type: 'decode' | 'protocol-refresh'];
}>();

const { decoding, loading, locations, onlyChains } = toRefs(props);

const { t } = useI18n();

const { resetUndecodedTransactionsStatus } = useHistoryStore();
const { protocolCacheStatus, receivingProtocolCacheStatus } = storeToRefs(useHistoryStore());
const { decodingStatus } = storeToRefs(useHistoryStore());

const {
  getKey: getTransactionKey,
  isQueryFinished: isTransactionQueryFinished,
  resetQueryStatus: resetTransactionsQueryStatus,
  sortedQueryStatus: transactions,
} = useTransactionQueryStatus(onlyChains);

const {
  getKey: getEventKey,
  isQueryFinished: isEventQueryFinished,
  resetQueryStatus: resetEventsQueryStatus,
  sortedQueryStatus: events,
} = useEventsQueryStatus(locations);
const { isTaskRunning } = useTaskStore();

const refreshProtocolCacheTaskRunning = isTaskRunning(TaskType.REFRESH_GENERAL_CACHE);
const items = computed(() => [...get(transactions), ...get(events)]);
const isQuery = computed(() => get(currentAction) === 'query');

const show = computed(() => get(loading) || get(decoding) || get(receivingProtocolCacheStatus) || get(items).length > 0);
const showDebounced = refDebounced(show, 400);
const usedShow = logicOr(show, showDebounced);

function getItemKey(item: EvmTransactionQueryData | HistoryEventsQueryData) {
  if ('eventType' in item)
    return getEventKey(item);

  return getTransactionKey(item);
}

function isItemQueryFinished(item: EvmTransactionQueryData | HistoryEventsQueryData) {
  if ('eventType' in item)
    return isEventQueryFinished(item);

  return isTransactionQueryFinished(item);
}

function resetQueryStatus() {
  resetTransactionsQueryStatus();
  resetEventsQueryStatus();
  resetUndecodedTransactionsStatus();
  set(currentAction, 'query');
}
</script>

<template>
  <HistoryQueryStatusBar
    v-if="usedShow"
    :colspan="colspan"
    :finished="isQuery ? !loading : !receivingProtocolCacheStatus && !decoding"
    @reset="resetQueryStatus()"
  >
    <template #current>
      <EventsCacheRefreshStatusCurrent v-if="refreshProtocolCacheTaskRunning" />
      <HistoryQueryStatusCurrent
        v-else-if="isQuery"
        :finished="!loading"
      />
      <EventsDecodingStatusCurrent
        v-else
        :finished="!decoding"
      />
    </template>

    <template #dialog>
      <HistoryQueryStatusDialog
        v-if="isQuery && !refreshProtocolCacheTaskRunning"
        :only-chains="onlyChains"
        :locations="locations"
        :events="events"
        :transactions="transactions"
        :decoding-status="decodingStatus"
        :loading="loading"
        :protocol-cache-status="protocolCacheStatus"
        :get-key="getItemKey"
        :is-item-finished="isItemQueryFinished"
      />

      <RuiTooltip
        v-else
        :popper="{ placement: 'top' }"
        :open-delay="400"
        class="ml-4"
      >
        <template #activator>
          <RuiButton
            variant="text"
            icon
            size="sm"
            class="!p-2"
            @click="emit('show:dialog', refreshProtocolCacheTaskRunning ? 'protocol-refresh' : 'decode')"
          >
            <template #append>
              <RuiIcon name="lu-info" />
            </template>
          </RuiButton>
        </template>
        {{ t('common.details') }}
      </RuiTooltip>
    </template>
  </HistoryQueryStatusBar>
</template>
