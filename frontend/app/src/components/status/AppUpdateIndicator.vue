<script setup lang="ts">
import { startPromise } from '@shared/utils';
import { useSessionStore } from '@/store/session';
import { useFrontendSettingsStore } from '@/store/settings/frontend';
import { useMainStore } from '@/store/main';
import { useInterop } from '@/composables/electron-interop';

const mainStore = useMainStore();
const { updateNeeded, version } = storeToRefs(mainStore);
const { getVersion } = mainStore;
const { isPackaged, openUrl } = useInterop();
const { versionUpdateCheckFrequency } = storeToRefs(useFrontendSettingsStore());
const { showUpdatePopup } = storeToRefs(useSessionStore());

const appVersion = computed(() => get(version).latestVersion);

const openLink = () => openUrl(get(version).downloadUrl);

function openUpdatePopup() {
  set(showUpdatePopup, true);
}

function update() {
  if (isPackaged)
    openUpdatePopup();
  else openLink();
}

const period = get(versionUpdateCheckFrequency) * 60 * 60 * 1000;

const { isActive, pause, resume } = useIntervalFn(() => {
  startPromise(getVersion());
}, period, { immediate: false });

function setVersionUpdateCheckInterval() {
  if (isActive)
    pause();

  if (period > 0)
    resume();
}

onMounted(() => {
  setVersionUpdateCheckInterval();
});

watch(versionUpdateCheckFrequency, () => setVersionUpdateCheckInterval());

const { t } = useI18n();
</script>

<template>
  <RuiTooltip
    v-if="updateNeeded"
    :open-delay="400"
  >
    <template #activator>
      <RuiButton
        color="info"
        icon
        @click="update()"
      >
        <RuiIcon name="lu-circle-arrow-up" />
      </RuiButton>
    </template>
    {{ t('update_indicator.version', { appVersion }) }}
  </RuiTooltip>
</template>
