<script setup lang="ts">
import { useAccountingSettingsStore } from '@/store/settings/accounting';
import SettingsOption from '@/components/settings/controls/SettingsOption.vue';

const calculatePastCostBasis = ref(false);
const { calculatePastCostBasis: enabled } = storeToRefs(useAccountingSettingsStore());
const { t } = useI18n();

function switchSuccessMessage(enabled: boolean) {
  return enabled
    ? t('account_settings.messages.cost_basis.enabled')
    : t('account_settings.messages.cost_basis.disabled');
}

onMounted(() => {
  set(calculatePastCostBasis, get(enabled));
});
</script>

<template>
  <SettingsOption
    #default="{ error, success, update }"
    setting="calculatePastCostBasis"
    :error-message="t('account_settings.messages.cost_basis.error')"
    :success-message="switchSuccessMessage"
  >
    <RuiSwitch
      v-model="calculatePastCostBasis"
      :success-messages="success"
      :error-messages="error"
      :label="t('accounting_settings.trade.labels.calculate_past_cost_basis')"
      color="primary"
      @update:model-value="update($event)"
    />
  </SettingsOption>
</template>
