<script setup lang="ts">
import { NoteLocation } from '@/types/notes';
import { usePremium } from '@/composables/premium';
import WrappedContainer from '@/components/wrapped/WrappedContainer.vue';
import WrappedContainerPlaceholder from '@/components/wrapped/WrappedContainerPlaceholder.vue';

definePage({
  meta: {
    noteLocation: NoteLocation.STATISTICS_HISTORY_EVENTS,
  },
  name: 'statistics-history-events',
});

const premium = usePremium();
</script>

<template>
  <div class="container">
    <RuiCard class="max-w-[800px] mx-auto">
      <WrappedContainer v-if="premium" />
      <WrappedContainerPlaceholder v-else />
    </RuiCard>
  </div>
</template>
