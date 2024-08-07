<script setup lang="ts">
import { objectOmit } from '@vueuse/core';
import XpubInput from '@/components/accounts/blockchain/XpubInput.vue';
import type { ValidationErrors } from '@/types/api/errors';
import type { XpubPayload } from '@/types/blockchain/accounts';
import type { XpubManage } from '@/composables/accounts/blockchain/use-account-manage';

const props = defineProps<{
  value: XpubManage;
  loading: boolean;
  errorMessages: ValidationErrors;
}>();

const emit = defineEmits<{
  (e: 'input', value: XpubManage): void;
  (e: 'update:error-messages', value: ValidationErrors): void;
}>();

const { value: modelValue } = toRefs(props);

const input = ref<InstanceType<typeof XpubInput>>();

const errors = useKebabVModel(props, 'errorMessages', emit);

function updateVModel(value: XpubManage) {
  emit('input', value);
}

const xpub = computed<XpubPayload>({
  get() {
    const model = get(modelValue);
    return model.data.xpub;
  },
  set(xpub: XpubPayload) {
    const model = get(modelValue);
    updateVModel({
      ...model,
      data: {
        ...model.data,
        xpub,
      },
    });
  },
});

const tags = computed<string[]>({
  get() {
    return get(modelValue).data.tags ?? [];
  },
  set(tags: string[]) {
    const model = get(modelValue);
    updateVModel({
      ...model,
      data: {
        ...model.data,
        tags: tags.length > 0 ? tags : null,
      },
    });
  },
});

const label = computed<string>({
  get() {
    return get(modelValue).data.label ?? '';
  },
  set(label: string) {
    const model = get(modelValue);
    const labelData = label ? { label } : {};
    updateVModel({
      ...model,
      data: {
        ...objectOmit(model.data, ['label']),
        ...labelData,
      },
    });
  },
});

function validate(): Promise<boolean> {
  assert(isDefined(input));
  return get(input).validate();
}

defineExpose({
  validate,
});
</script>

<template>
  <div class="flex flex-col gap-4">
    <XpubInput
      ref="input"
      :disabled="loading || value.mode === 'edit'"
      :error-messages.sync="errors"
      :xpub.sync="xpub"
      :blockchain="value.chain"
    />
    <AccountDataInput
      :tags.sync="tags"
      :label.sync="label"
      :disabled="loading"
    />
  </div>
</template>
