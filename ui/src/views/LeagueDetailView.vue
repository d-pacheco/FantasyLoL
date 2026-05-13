<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const leagueId = route.params.id as string
</script>

<template>
  <div class="flex flex-col gap-6">
    <div>
      <h2 class="text-lg font-semibold text-foreground">League Details</h2>
      <p class="mt-1 text-sm text-foreground-muted">League ID: {{ leagueId }}</p>
    </div>
    <div class="rounded-xl border border-border-subtle bg-surface px-6 py-10 text-center">
      <p class="text-foreground-muted text-sm">League details coming soon.</p>
    </div>
  </div>
</template>
