<script setup lang="ts">
import useVuelidate from '@vuelidate/core';
import { and, helpers, minValue, numeric, required } from '@vuelidate/validators';
import { isEqual } from 'es-toolkit';
import { LogLevel } from '@shared/log-level';
import { toMessages } from '@/utils/validation';
import { useMainStore } from '@/store/main';
import { useConfirmStore } from '@/store/confirm';
import { useBackendManagement } from '@/composables/backend';
import { useInterop } from '@/composables/electron-interop';
import { useSettingsApi } from '@/composables/api/settings/settings-api';
import SettingResetButton from '@/components/settings/SettingResetButton.vue';
import LanguageSetting from '@/components/settings/general/language/LanguageSetting.vue';
import BigDialog from '@/components/dialogs/BigDialog.vue';
import type { RuiIcons } from '@rotki/ui-library';
import type { BackendOptions } from '@shared/ipc';
import type { Writeable } from '@rotki/common';
import type { BackendConfiguration } from '@/types/backend';

const emit = defineEmits<{
  (e: 'dismiss'): void;
}>();

const { t } = useI18n();

const { dataDirectory, defaultBackendArguments } = storeToRefs(useMainStore());

const userDataDirectory = ref<string>('');
const userLogDirectory = ref<string>('');
const logFromOtherModules = ref<boolean>(false);
const valid = ref<boolean>(false);

const maxLogSize = ref<string>('0');
const sqliteInstructions = ref<string>('0');
const maxLogFiles = ref<string>('0');

const { backendSettings } = useSettingsApi();

const selecting = ref<boolean>(false);
const confirmReset = ref<boolean>(false);
const configuration = asyncComputed<BackendConfiguration>(() => backendSettings());

function parseValue(value?: string) {
  if (!value)
    return 0;

  const parsedValue = Number.parseInt(value);
  return Number.isNaN(parsedValue) ? 0 : parsedValue;
}

function stringifyValue(value?: number) {
  if (!value)
    return '0';

  return value.toString();
}

const { defaultLogDirectory, defaultLogLevel, fileConfig, logLevel, options, resetOptions, saveOptions }
  = useBackendManagement(loaded);

const initialOptions = computed<Partial<BackendOptions>>(() => {
  const config = get(configuration);
  const opts = get(options);
  const defaults = get(defaultBackendArguments);
  return {
    dataDirectory: opts.dataDirectory ?? get(dataDirectory),
    logDirectory: opts.logDirectory ?? get(defaultLogDirectory),
    logFromOtherModules: opts.logFromOtherModules ?? false,
    loglevel: opts.loglevel ?? get(defaultLogLevel),
    maxLogfilesNum: opts.maxLogfilesNum ?? config?.maxLogfilesNum?.value ?? defaults.maxLogfilesNum,
    maxSizeInMbAllLogs: opts.maxSizeInMbAllLogs ?? config?.maxSizeInMbAllLogs?.value ?? defaults.maxSizeInMbAllLogs,
    sqliteInstructions: opts.sqliteInstructions ?? config?.sqliteInstructions?.value ?? defaults.sqliteInstructions,
  };
});

function loaded() {
  const initial = get(initialOptions);

  set(logLevel, initial.loglevel);
  set(userDataDirectory, initial.dataDirectory);
  set(userLogDirectory, initial.logDirectory);
  set(logFromOtherModules, initial.logFromOtherModules);
  set(maxLogFiles, stringifyValue(initial.maxLogfilesNum));
  set(maxLogSize, stringifyValue(initial.maxSizeInMbAllLogs));
  set(sqliteInstructions, stringifyValue(initial.sqliteInstructions));
}

const isMaxLogFilesDefault = computed(() => {
  const defaults = get(defaultBackendArguments);
  return defaults.maxLogfilesNum === parseValue(get(maxLogFiles));
});

const isMaxSizeDefault = computed(() => {
  const defaults = get(defaultBackendArguments);
  return defaults.maxSizeInMbAllLogs === parseValue(get(maxLogSize));
});

const isSqliteInstructionsDefaults = computed(() => {
  const defaults = get(defaultBackendArguments);
  return defaults.sqliteInstructions === parseValue(get(sqliteInstructions));
});

function resetDefaultArguments(field: 'files' | 'size' | 'instructions') {
  const defaults = get(defaultBackendArguments);
  if (field === 'files')
    set(maxLogFiles, stringifyValue(defaults.maxLogfilesNum));
  else if (field === 'size')
    set(maxLogSize, stringifyValue(defaults.maxSizeInMbAllLogs));
  else if (field === 'instructions')
    set(sqliteInstructions, stringifyValue(defaults.sqliteInstructions));
}

const newUserOptions = computed(() => {
  const initial = get(initialOptions);
  const newOptions: Writeable<Partial<BackendOptions>> = {};

  const level = get(logLevel);
  if (level !== initial.loglevel)
    newOptions.loglevel = level;

  const userData = get(userDataDirectory);
  if (userData !== initial.dataDirectory)
    newOptions.dataDirectory = userData;

  const userLog = get(userLogDirectory);
  if (userLog !== initial.logDirectory)
    newOptions.logDirectory = userLog;

  const logFromOther = get(logFromOtherModules);
  if (logFromOther !== initial.logFromOtherModules)
    newOptions.logFromOtherModules = logFromOther;

  if (!get(isMaxLogFilesDefault))
    newOptions.maxLogfilesNum = parseValue(get(maxLogFiles));

  if (!get(isMaxSizeDefault))
    newOptions.maxSizeInMbAllLogs = parseValue(get(maxLogSize));

  if (!get(isSqliteInstructionsDefaults))
    newOptions.sqliteInstructions = parseValue(get(sqliteInstructions));

  return newOptions;
});

const anyValueChanged = computed(() => {
  const form: Partial<BackendOptions> = {
    dataDirectory: get(userDataDirectory),
    logDirectory: get(userLogDirectory),
    logFromOtherModules: get(logFromOtherModules),
    loglevel: get(logLevel),
    maxLogfilesNum: parseValue(get(maxLogFiles)),
    maxSizeInMbAllLogs: parseValue(get(maxLogSize)),
    sqliteInstructions: parseValue(get(sqliteInstructions)),
  };

  return !isEqual(form, get(initialOptions));
});

const { openDirectory } = useInterop();

const nonNegativeNumberRules = {
  nonNegative: helpers.withMessage(t('backend_settings.errors.min', { min: 0 }), and(numeric, minValue(0))),
  required: helpers.withMessage(t('backend_settings.errors.non_empty'), required),
};

const rules = {
  maxLogFiles: nonNegativeNumberRules,
  maxLogSize: nonNegativeNumberRules,
  sqliteInstructions: nonNegativeNumberRules,
};

const v$ = useVuelidate(
  rules,
  {
    maxLogFiles,
    maxLogSize,
    sqliteInstructions,
  },
  { $autoDirty: true },
);

watch(v$, ({ $invalid }) => {
  set(valid, !$invalid);
});

function icon(level: LogLevel): RuiIcons {
  if (level === LogLevel.DEBUG)
    return 'lu-bug';
  else if (level === LogLevel.INFO)
    return 'lu-info';
  else if (level === LogLevel.WARNING)
    return 'lu-triangle-alert';
  else if (level === LogLevel.ERROR)
    return 'lu-circle-alert';
  else if (level === LogLevel.CRITICAL)
    return 'lu-skull';
  else if (level === LogLevel.TRACE)
    return 'lu-file-search';

  throw new Error(`Invalid option: ${level}`);
}

const reset = async function () {
  set(confirmReset, false);
  dismiss();
  await resetOptions();
};

const selectDataDirectory = async function () {
  if (get(selecting))
    return;

  try {
    const title = t('backend_settings.data_directory.select');
    const directory = await openDirectory(title);
    if (directory)
      set(userDataDirectory, directory);
  }
  finally {
    set(selecting, false);
  }
};

async function save() {
  dismiss();
  await saveOptions(get(newUserOptions));
}

async function selectLogsDirectory() {
  if (get(selecting))
    return;

  set(selecting, true);
  try {
    const directory = await openDirectory(t('backend_settings.log_directory.select'));
    if (directory)
      set(userLogDirectory, directory);
  }
  finally {
    set(selecting, false);
  }
}

function dismiss() {
  emit('dismiss');
}

watch(dataDirectory, (directory) => {
  set(userDataDirectory, get(options).dataDirectory ?? directory);
});

const levels = Object.values(LogLevel);

const { show } = useConfirmStore();

function showResetConfirmation() {
  show(
    {
      message: t('backend_settings.confirm.message'),
      title: t('backend_settings.confirm.title'),
    },
    reset,
  );
}

const [CreateLabel, ReuseLabel] = createReusableTemplate<{ item: LogLevel }>();
</script>

<template>
  <BigDialog
    display
    :title="t('frontend_settings.title')"
    @cancel="dismiss()"
  >
    <div class="mb-4">
      <LanguageSetting use-local-setting />
    </div>

    <div class="mb-4">
      <RuiCardHeader class="p-0">
        <template #header>
          {{ t('backend_settings.title') }}
        </template>
        <template #subheader>
          {{ t('backend_settings.subtitle') }}
        </template>
      </RuiCardHeader>
    </div>

    <div class="flex flex-col gap-4">
      <CreateLabel #default="{ item }">
        <div class="flex items-center gap-3">
          <RuiIcon
            class="text-rui-text-secondary"
            :name="icon(item)"
          />
          <span class="capitalize"> {{ item }} </span>
        </div>
      </CreateLabel>
      <RuiTextField
        v-model="userDataDirectory"
        data-cy="user-data-directory-input"
        :loading="!userDataDirectory"
        class="pt-2"
        variant="outlined"
        color="primary"
        :disabled="!!fileConfig.dataDirectory || !userDataDirectory"
        :hint="
          !!fileConfig.dataDirectory
            ? t('backend_settings.config_file_disabled')
            : t('backend_settings.settings.data_directory.hint')
        "
        :label="t('backend_settings.settings.data_directory.label')"
        readonly
        @click="selectDataDirectory()"
      >
        <template #append>
          <RuiButton
            variant="text"
            icon
            :disabled="!userDataDirectory"
            @click="selectDataDirectory()"
          >
            <RuiIcon name="lu-folder" />
          </RuiButton>
        </template>
      </RuiTextField>
      <RuiTextField
        v-model="userLogDirectory"
        data-cy="user-log-directory-input"
        :disabled="!!fileConfig.logDirectory"
        :hint="!!fileConfig.logDirectory ? t('backend_settings.config_file_disabled') : undefined"
        variant="outlined"
        color="primary"
        :label="t('backend_settings.settings.log_directory.label')"
        readonly
        @click="selectLogsDirectory()"
      >
        <template #append>
          <RuiButton
            variant="text"
            icon
            @click="selectLogsDirectory()"
          >
            <RuiIcon name="lu-folder" />
          </RuiButton>
        </template>
      </RuiTextField>

      <RuiMenuSelect
        v-model="logLevel"
        :options="levels"
        class="loglevel-input"
        :disabled="!!fileConfig.loglevel"
        :label="t('backend_settings.settings.log_level.label')"
        :hide-details="!fileConfig.loglevel"
        :hint="!!fileConfig.loglevel ? t('backend_settings.config_file_disabled') : undefined"
        variant="outlined"
      >
        <template #item="{ item }">
          <ReuseLabel :item="item" />
        </template>

        <template #selection="{ item }">
          <ReuseLabel :item="item" />
        </template>
      </RuiMenuSelect>
    </div>

    <RuiAccordions>
      <RuiAccordion
        data-cy="onboarding-setting__advance"
        header-class="py-4"
        eager
      >
        <template #header>
          {{ t('backend_settings.advanced') }}
        </template>
        <div class="py-2">
          <RuiTextField
            v-model="maxLogSize"
            data-cy="max-log-size-input"
            class="mb-4"
            variant="outlined"
            color="primary"
            :hint="
              !!fileConfig.maxSizeInMbAllLogs
                ? t('backend_settings.config_file_disabled')
                : t('backend_settings.max_log_size.hint')
            "
            :label="t('backend_settings.max_log_size.label')"
            :disabled="!!fileConfig.maxSizeInMbAllLogs"
            :loading="!configuration || !defaultBackendArguments"
            :error-messages="toMessages(v$.maxLogSize)"
            type="number"
          >
            <template #append>
              <SettingResetButton
                v-if="!isMaxSizeDefault"
                data-cy="reset-max-log-size"
                @click="resetDefaultArguments('size')"
              />
            </template>
          </RuiTextField>
          <RuiTextField
            v-model="maxLogFiles"
            data-cy="max-log-files-input"
            variant="outlined"
            color="primary"
            class="mb-4"
            :hint="t('backend_settings.max_log_files.hint')"
            :label="
              !!fileConfig.maxLogfilesNum
                ? t('backend_settings.config_file_disabled')
                : t('backend_settings.max_log_files.label')
            "
            :disabled="!!fileConfig.maxLogfilesNum"
            :loading="!configuration || !defaultBackendArguments"
            :error-messages="toMessages(v$.maxLogFiles)"
            type="number"
          >
            <template #append>
              <SettingResetButton
                v-if="!isMaxLogFilesDefault"
                data-cy="reset-max-log-files"
                @click="resetDefaultArguments('files')"
              />
            </template>
          </RuiTextField>

          <RuiTextField
            v-model="sqliteInstructions"
            data-cy="sqlite-instructions-input"
            variant="outlined"
            color="primary"
            class="mb-4"
            :hint="
              !!fileConfig.sqliteInstructions
                ? t('backend_settings.config_file_disabled')
                : t('backend_settings.sqlite_instructions.hint')
            "
            :label="t('backend_settings.sqlite_instructions.label')"
            :disabled="!!fileConfig.sqliteInstructions"
            :loading="!configuration || !defaultBackendArguments"
            :error-messages="toMessages(v$.sqliteInstructions)"
            type="number"
          >
            <template #append>
              <SettingResetButton
                v-if="!isSqliteInstructionsDefaults"
                data-cy="reset-sqlite-instructions"
                @click="resetDefaultArguments('instructions')"
              />
            </template>
          </RuiTextField>

          <RuiCheckbox
            v-model="logFromOtherModules"
            color="primary"
            data-cy="log-from-other-modules-checkbox"
            :label="t('backend_settings.log_from_other_modules.label')"
            :disabled="fileConfig.logFromOtherModules"
            :hint="
              fileConfig.logFromOtherModules
                ? t('backend_settings.config_file_disabled')
                : t('backend_settings.log_from_other_modules.hint')
            "
          >
            {{ t('backend_settings.log_from_other_modules.label') }}
          </RuiCheckbox>
        </div>
      </RuiAccordion>
    </RuiAccordions>

    <template #footer>
      <div class="flex justify-end w-full gap-2">
        <RuiButton
          variant="text"
          color="primary"
          @click="dismiss()"
        >
          {{ t('common.actions.cancel') }}
        </RuiButton>
        <RuiButton
          variant="outlined"
          color="primary"
          @click="showResetConfirmation()"
        >
          {{ t('backend_settings.actions.reset') }}
        </RuiButton>
        <RuiButton
          data-cy="onboarding-setting__submit-button"
          color="primary"
          :disabled="!anyValueChanged || !valid"
          @click="save()"
        >
          {{ t('common.actions.save') }}
        </RuiButton>
      </div>
    </template>
  </BigDialog>
</template>
