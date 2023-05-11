<script setup lang="ts">
import { type Ref } from 'vue';
import { RefreshableCache } from '@/types/session/purge';

const { tc } = useI18n();

const refreshable = [
  {
    id: RefreshableCache.GENERAL_CACHE,
    text: tc('data_management.refresh_cache.label.general_cache')
  }
];

const source: Ref<RefreshableCache> = ref(RefreshableCache.GENERAL_CACHE);

const { refreshGeneralCache } = useSessionPurge();

const refreshSource = async (source: RefreshableCache) => {
  if (source === RefreshableCache.GENERAL_CACHE) {
    await refreshGeneralCache();
  }
};

const { status, pending, showConfirmation } = useCacheClear<RefreshableCache>(
  refreshable,
  refreshSource,
  (source: string) => ({
    success: tc('data_management.refresh_cache.success', 0, {
      source
    }),
    error: tc('data_management.refresh_cache.error', 0, {
      source
    })
  }),
  (source: string) => ({
    title: tc('data_management.refresh_cache.confirm.title'),
    message: tc('data_management.refresh_cache.confirm.message', 0, {
      source
    })
  })
);
</script>

<template>
  <div class="mb-2">
    <div class="mb-6">
      <div class="text-h6">
        {{ tc('data_management.refresh_cache.title') }}
      </div>
      <div>
        {{ tc('data_management.refresh_cache.subtitle') }}
      </div>
    </div>

    <v-row class="mb-0" align="center">
      <v-col>
        <v-autocomplete
          v-model="source"
          outlined
          :label="tc('data_management.refresh_cache.select_cache')"
          :items="refreshable"
          item-text="text"
          item-value="id"
          hide-details
          :disabled="pending"
        />
      </v-col>

      <v-col cols="auto">
        <v-tooltip open-delay="400" top>
          <template #activator="{ on, attrs }">
            <v-btn
              v-bind="attrs"
              icon
              :disabled="!source || pending"
              :loading="pending"
              v-on="on"
              @click="showConfirmation(source)"
            >
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </template>
          <span> {{ tc('data_management.refresh_cache.tooltip') }} </span>
        </v-tooltip>
      </v-col>
    </v-row>

    <action-status-indicator v-if="status" :status="status" />
  </div>
</template>