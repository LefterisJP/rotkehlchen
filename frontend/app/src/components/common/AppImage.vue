<script setup lang="ts">
import { toRem } from '@/utils/data';
import type { MaybeRef } from '@vueuse/core';

const props = withDefaults(
  defineProps<{
    width?: string | number;
    height?: string | number;
    maxWidth?: string | number;
    maxHeight?: string | number;
    size?: string | number;
    src?: string;
    srcset?: string;
    sizes?: string;
    alt?: string;
    contain?: boolean;
    loading?: boolean;
  }>(),
  {
    alt: undefined,
    contain: false,
    height: undefined,
    loading: false,
    maxHeight: undefined,
    maxWidth: undefined,
    size: undefined,
    sizes: undefined,
    src: undefined,
    srcset: undefined,
    width: undefined,
  },
);

const emit = defineEmits<{
  (e: 'error'): void;
  (e: 'load'): void;
  (e: 'loadstart'): void;
}>();

const { height, maxHeight, maxWidth, size, width } = toRefs(props);

const error = ref<boolean>(false);
const success = ref<boolean>(false);

const style = computed(() => ({
  height: getSizeOrValue(height),
  maxHeight: getSizeOrValue(maxHeight),
  maxWidth: getSizeOrValue(maxWidth),
  width: getSizeOrValue(width),
}));

function getSizeOrValue(value: MaybeRef<string | number | undefined>) {
  return isDefined(get(size)) ? toRem(get(size)) : toRem(get(value));
}

function onError() {
  set(error, true);
  emit('error');
}

function onLoad() {
  set(error, false);
  set(success, true);
  emit('load');
}

function onLoadStart() {
  set(error, false);
  emit('loadstart');
}
</script>

<template>
  <div class="flex">
    <RuiSkeletonLoader
      v-if="loading"
      :style="style"
    />
    <img
      v-else-if="error"
      src="/assets/images/placeholder/image.svg"
      :class="{ 'object-contain': contain }"
      loading="lazy"
      :style="style"
      :sizes="sizes"
      :srcset="srcset"
    />
    <img
      v-else
      :alt="alt"
      :class="{ 'object-contain': contain }"
      :style="style"
      :src="src"
      :sizes="sizes"
      :srcset="srcset"
      loading="lazy"
      @error="onError()"
      @loadstart="onLoadStart()"
      @load="onLoad()"
    />
  </div>
</template>
