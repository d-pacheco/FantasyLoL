<script setup lang="ts">
import type { FantasyLeagueSettings } from '../../types/fantasy'

defineProps<{
  settings: FantasyLeagueSettings | null
  loading: boolean
  error: string
}>()
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>
    <div v-else-if="settings" class="flex flex-col gap-4">
      <div class="rounded-xl border border-border-subtle overflow-hidden">
        <table class="w-full">
          <tbody class="divide-y divide-border-subtle">
            <tr class="bg-surface">
              <td class="px-4 py-3 text-xs font-medium text-foreground-muted w-40">League Name</td>
              <td class="px-4 py-3 text-sm text-foreground">{{ settings.name }}</td>
            </tr>
            <tr class="bg-surface">
              <td class="px-4 py-3 text-xs font-medium text-foreground-muted">Number of Teams</td>
              <td class="px-4 py-3 text-sm text-foreground">{{ settings.number_of_teams }}</td>
            </tr>
            <tr class="bg-surface">
              <td class="px-4 py-3 text-xs font-medium text-foreground-muted">Available Leagues</td>
              <td class="px-4 py-3 text-sm text-foreground">{{ settings.available_leagues.join(', ') || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
