<script setup lang="ts">
import { useFrontendSettingsStore } from '@/store/settings/frontend';
import { useStatisticsStore } from '@/store/statistics';
import SettingsOption from '@/components/settings/controls/SettingsOption.vue';

const includeNfts = ref<boolean>(true);
const { fetchNetValue } = useStatisticsStore();
const { nftsInNetValue: enabled } = storeToRefs(useFrontendSettingsStore());

onMounted(() => {
  set(includeNfts, get(enabled));
});

const { t } = useI18n();
</script>

<template>
  <SettingsOption
    #default="{ error, success, update }"
    setting="nftsInNetValue"
    frontend-setting
    @finished="fetchNetValue()"
  >
    <RuiSwitch
      v-model="includeNfts"
      color="primary"
      :label="t('general_settings.nft_setting.label.include_nfts')"
      :success-messages="success"
      :error-messages="error"
      @update:model-value="update($event)"
    />
  </SettingsOption>
</template>
