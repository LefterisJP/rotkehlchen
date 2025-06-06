<script setup lang="ts">
import { uniqueStrings } from '@/utils/data';
import { getDomain } from '@/utils/url';
import { useConfirmStore } from '@/store/confirm';
import { useFrontendSettingsStore } from '@/store/settings/frontend';
import { useNftImage } from '@/composables/nft-image';
import IconLink from '@/components/base/IconLink.vue';
import AmountDisplay from '@/components/display/amount/AmountDisplay.vue';
import AppImage from '@/components/common/AppImage.vue';
import ExternalLink from '@/components/helper/ExternalLink.vue';
import type { GalleryNft } from '@/types/nfts';
import type { StyleValue } from 'vue';

const props = defineProps<{
  item: GalleryNft;
}>();

const { item } = toRefs(props);

const frontendStore = useFrontendSettingsStore();

const { whitelistedDomainsForNftImages } = storeToRefs(frontendStore);
const { updateSetting } = frontendStore;

const imageUrlSource = computed<string | null>(() => get(item).imageUrl);

const { isVideo, renderedMedia, shouldRender } = useNftImage(imageUrlSource);

const name = computed(() => (get(item).name ? get(item).name : get(item).collection.name));

const { t } = useI18n();

const domain = computed<string | null>(() => getDomain(get(imageUrlSource) || ''));

const { show } = useConfirmStore();

function showAllowDomainConfirmation() {
  show(
    {
      message: t(
        'general_settings.nft_setting.update_whitelist_confirmation.message',
        {
          domain: get(domain),
        },
        2,
      ),
      title: t('general_settings.nft_setting.update_whitelist_confirmation.title'),
    },
    allowDomain,
  );
}

function allowDomain() {
  const domainVal = get(domain);

  if (!domainVal)
    return;

  const newWhitelisted = [...get(whitelistedDomainsForNftImages), domainVal].filter(uniqueStrings);

  updateSetting({ whitelistedDomainsForNftImages: newWhitelisted });
}

const mediaStyle = computed<StyleValue>(() => {
  const backgroundColor = get(item).backgroundColor;
  if (!get(shouldRender) || !backgroundColor)
    return {};

  return { backgroundColor };
});
</script>

<template>
  <RuiCard
    no-padding
    class="mx-auto overflow-hidden"
  >
    <div class="relative flex">
      <RuiTooltip
        :popper="{ placement: 'top' }"
        :disabled="shouldRender"
        :open-delay="400"
        class="w-full"
        tooltip-class="max-w-[10rem]"
      >
        <template #activator>
          <ExternalLink
            :url="item.externalLink"
            class="w-full"
            custom
          >
            <video
              v-if="isVideo"
              controls
              width="auto"
              :src="renderedMedia"
              :style="mediaStyle"
              class="w-full"
              :class="$style.media"
            />
            <AppImage
              v-else
              :src="renderedMedia"
              contain
              :style="mediaStyle"
              width="100%"
              :class="$style.media"
            />
          </ExternalLink>
        </template>

        {{ t('nft_balance_table.hidden_hint') }}
      </RuiTooltip>

      <RuiTooltip
        v-if="!shouldRender"
        :popper="{ placement: 'top' }"
        :open-delay="400"
        :class="$style['unlock-button']"
      >
        <template #activator>
          <RuiButton
            class="!p-2"
            icon
            @click="showAllowDomainConfirmation()"
          >
            <RuiIcon
              name="lu-lock-keyhole-open"
              size="16"
            />
          </RuiButton>
        </template>
        {{ t('nft_gallery.allow_domain') }}
        <strong class="text-rui-warning-lighter">{{ domain }}</strong>
      </RuiTooltip>
    </div>
    <div class="p-4">
      <RuiTooltip
        :popper="{ placement: 'top' }"
        :open-delay="400"
        tooltip-class="max-w-[20rem]"
        class="text-truncate block text-subtitle-1 font-medium"
      >
        <template #activator>
          {{ name }}
        </template>
        {{ name }}
      </RuiTooltip>
      <RuiTooltip
        :popper="{ placement: 'top' }"
        :open-delay="400"
        tooltip-class="max-w-[20rem] text-truncate overflow-hidden"
        class="pt-1 text-truncate max-w-full"
      >
        <template #activator>
          <RuiChip
            tile
            size="sm"
            class="font-medium text-caption"
          >
            {{ item.collection.name }}
          </RuiChip>
        </template>
        {{ item.collection.description }}
      </RuiTooltip>
      <div class="pt-4 flex flex-col font-medium">
        <AmountDisplay
          :value="item.priceInAsset"
          :asset="item.priceAsset"
        />
        <AmountDisplay
          class="text-rui-text-secondary"
          :price-asset="item.priceAsset"
          :amount="item.priceInAsset"
          :value="item.priceUsd"
          show-currency="ticker"
          fiat-currency="USD"
        />
      </div>
    </div>
    <template #footer>
      <IconLink
        v-if="item.permalink"
        :url="item.permalink"
        class="-mt-2 -mx-1"
        text="OpenSea"
      />
    </template>
  </RuiCard>
</template>

<style lang="scss" module>
video {
  @apply max-w-full h-auto;
}

.unlock-button {
  @apply absolute right-2 bottom-2;
}

.media {
  @apply object-contain;
  aspect-ratio: 1 / 1;
}
</style>
