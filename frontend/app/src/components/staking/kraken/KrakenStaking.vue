<script setup lang="ts">
import { type AssetBalance, HistoryEventEntryType } from '@rotki/common';
import { useKrakenStakingStore } from '@/store/staking/kraken';
import HistoryEventsView from '@/components/history/events/HistoryEventsView.vue';
import KrakenStakingReceived from '@/components/staking/kraken/KrakenStakingReceived.vue';
import KrakenStakingOverview from '@/components/staking/kraken/KrakenStakingOverview.vue';
import KrakenDateFilter from '@/components/staking/kraken/KrakenDateFilter.vue';
import { useBalancePricesStore } from '@/store/balances/prices';
import { useHistoricCachePriceStore } from '@/store/prices/historic';
import type { KrakenStakingDateFilter } from '@/types/staking';

const modelValue = defineModel<KrakenStakingDateFilter>({ required: true });

defineProps<{
  loading: boolean;
}>();

const { t } = useI18n();

const { events } = toRefs(useKrakenStakingStore());
const { assetPrice } = useBalancePricesStore();

const { getProtocolStatsPriceQueryStatus } = useHistoricCachePriceStore();
const krakenHistoricPriceStatus = getProtocolStatsPriceQueryStatus('kraken');

const earnedAssetsData = computed<[boolean, AssetBalance[]]>(() => {
  const earned = get(events).received;

  let loading = false;

  const earnedWithPrice = earned.map((item) => {
    const price = get(assetPrice(item.asset));
    if (!price) {
      loading = true;

      return item;
    }
    return {
      ...item,
      usdValue: price.times(item.amount),
    };
  });

  return [loading, earnedWithPrice];
});
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="grid md:grid-cols-2 gap-x-4 gap-y-2">
      <KrakenDateFilter v-model="modelValue" />

      <div
        v-if="loading && krakenHistoricPriceStatus"
        class="flex items-center gap-2 text-rui-text-secondary text-sm"
      >
        <RuiProgress
          thickness="2"
          size="18"
          color="primary"
          variant="indeterminate"
          circular
        />
        {{ t('kraken_staking_events.query_historical_price', {
          processed: krakenHistoricPriceStatus.processed,
          total: krakenHistoricPriceStatus.total,
        }) }}
      </div>
    </div>
    <div class="grid md:grid-cols-2 gap-4">
      <KrakenStakingOverview
        :loading="earnedAssetsData[0]"
        :total-usd-historical="events.totalUsdValue"
        :earned="earnedAssetsData[1]"
      />
      <KrakenStakingReceived
        :loading="earnedAssetsData[0]"
        :received="earnedAssetsData[1]"
      />
    </div>

    <!-- as an exception here we specify event-types to only include staking events  -->
    <!-- if an alternative way becomes possible we can use that -->
    <HistoryEventsView
      use-external-account-filter
      location="kraken"
      :period="modelValue"
      :event-types="['staking']"
      :entry-types="[HistoryEventEntryType.HISTORY_EVENT]"
    />
  </div>
</template>
