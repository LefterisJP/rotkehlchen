<script setup lang="ts">
import { CURRENCY_USD } from '@/types/currencies';
import { useAssetPageNavigation } from '@/composables/assets/navigation';
import { useRefMap } from '@/composables/utils/useRefMap';
import { useAssetInfoRetrieval } from '@/composables/assets/retrieval';
import AmountDisplay from '@/components/display/amount/AmountDisplay.vue';
import AssetIcon from '@/components/helper/display/icons/AssetIcon.vue';
import type { HistoryEventEntry } from '@/types/history/events';

const props = defineProps<{
  event: HistoryEventEntry;
}>();

const { event } = toRefs(props);
const { assetSymbol } = useAssetInfoRetrieval();

const showBalance = computed<boolean>(() => get(event).eventType !== 'informational');

const eventAsset = useRefMap(event, ({ asset }) => asset);

const symbol = assetSymbol(eventAsset, {
  collectionParent: false,
});
const { navigateToDetails } = useAssetPageNavigation(eventAsset);
</script>

<template>
  <div class="py-2 flex items-center gap-2">
    <AssetIcon
      size="32px"
      :identifier="event.asset"
      :resolution-options="{
        collectionParent: false,
      }"
      @click="navigateToDetails()"
    />
    <div
      v-if="showBalance"
      class="flex flex-col"
    >
      <AmountDisplay
        :value="event.amount"
        :asset="event.asset"
        :resolution-options="{
          collectionParent: false,
        }"
      />
      <AmountDisplay
        :key="event.timestamp"
        :amount="event.amount"
        :value="Zero"
        :price-asset="event.asset"
        :fiat-currency="CURRENCY_USD"
        class="text-rui-text-secondary"
        :timestamp="event.timestamp"
        milliseconds
      />
    </div>
    <div
      v-else
      class="text-truncate"
    >
      {{ symbol }}
    </div>
  </div>
</template>
