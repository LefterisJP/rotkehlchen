<script setup lang="ts">
import { truncateAddress } from '@/utils/truncate';
import { useLinks } from '@/composables/links';
import { useInterop } from '@/composables/electron-interop';

defineOptions({
  inheritAttrs: false,
});

const props = withDefaults(
  defineProps<{
    url?: string;
    truncate?: boolean;
    text?: string;
    custom?: boolean;
    premium?: boolean;
  }>(),
  {
    custom: false,
    premium: false,
    text: '',
    truncate: false,
    url: undefined,
  },
);

const { text, truncate, url } = toRefs(props);
const { isPackaged } = useInterop();

const { href, linkTarget, onLinkClick } = useLinks(url);

const displayText = computed(() => (get(truncate) ? truncateAddress(get(text)) : get(text)));
</script>

<template>
  <RuiButton
    v-if="(url || premium) && !custom"
    :tag="isPackaged ? 'button' : 'a'"
    :href="href"
    :target="linkTarget"
    v-bind="$attrs"
    variant="text"
    :class="$style.button"
    @click="onLinkClick()"
  >
    <slot>{{ displayText }}</slot>
    <template
      v-for="(_, name) in $slots"
      #[name]="slotData"
      :key="name"
    >
      <slot
        :name="name"
        v-bind="slotData"
      />
    </template>
  </RuiButton>
  <a
    v-else-if="url || premium"
    :href="href"
    :target="linkTarget"
    class="whitespace-nowrap"
    v-bind="$attrs"
    @click="onLinkClick()"
  >
    <slot>{{ displayText }}</slot>
  </a>
  <div
    v-else
    v-bind="$attrs"
  >
    <slot />
  </div>
</template>

<style lang="scss" module>
.button {
  @apply inline text-[1em] p-0 px-0.5 -mx-0.5 #{!important};

  font-weight: inherit !important;

  span {
    @apply underline;
  }
}
</style>
