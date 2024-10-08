<script setup lang="ts">
import AutoDetectTokensSetting from '@/components/settings/general/AutoDetectTokensSetting.vue';
import { NoteLocation } from '@/types/notes';

definePage({
  meta: {
    noteLocation: NoteLocation.SETTINGS_GENERAL,
  },
});

const amountExample = bigNumberify(123456.789);
const { t } = useI18n();
</script>

<template>
  <div class="general-settings flex flex-col gap-8">
    <SettingCategory>
      <template #title>
        {{ t('general_settings.title') }}
      </template>

      <div class="flex flex-col gap-4">
        <UsageAnalyticsSetting />
        <LanguageSetting />
        <VersionUpdateFrequencySetting />
        <BalanceSaveFrequencySetting />
        <AutoDetectTokensSetting />
        <DateDisplayFormatSetting />
        <DateInputFormatSetting />
        <DisplayDateInLocaltimeSetting />
        <CsvExportDelimiterSetting />
        <BtcDerivationGapLimitSetting />
        <TreatEthAsEth2Setting />
        <EvmChainsToIgnoreSettings />
        <AskUserUponSizeDiscrepancySetting />
      </div>
    </SettingCategory>

    <SettingCategory>
      <template #title>
        {{ t('general_settings.amount.title') }}
      </template>

      <MainCurrencySetting class="mb-4" />
      <div class="grid sm:grid-cols-3 gap-4">
        <FloatingPrecisionSetting />
        <NumericSeparatorsSettings />
      </div>
      <AbbreviateNumberSetting />
      <CurrencyLocationSetting />

      <div>
        <strong>
          {{ t('general_settings.amount.label.resulting_format') }}
        </strong>
        <AmountDisplay
          :value="amountExample"
          show-currency="symbol"
        />
      </div>

      <RoundingSettings />
    </SettingCategory>

    <RpcSettings />
    <PriceOracleSettings />
    <NftSettings />
    <ExternalServiceSettings />
    <FrontendSettings />
  </div>
</template>

<style scoped lang="scss">
.general-settings {
  &__currency-list {
    font-size: 2em;
    font-weight: bold;
  }

  &__timeframe {
    min-height: 55px;
  }

  &__date-restore {
    margin-top: -6px;
  }
}
</style>
