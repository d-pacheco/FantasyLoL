<script setup lang="ts">
import type { FantasyLeagueScoringSettings } from '../../types/fantasy'

defineProps<{
  scoring: FantasyLeagueScoringSettings | null
  loading: boolean
  error: string
}>()

const labels: { key: keyof FantasyLeagueScoringSettings; label: string }[] = [
  { key: 'kills', label: 'Kills' },
  { key: 'deaths', label: 'Deaths' },
  { key: 'assists', label: 'Assists' },
  { key: 'creep_score', label: 'Creep Score' },
  { key: 'wards_placed', label: 'Wards Placed' },
  { key: 'wards_destroyed', label: 'Wards Destroyed' },
  { key: 'kill_participation', label: 'Kill Participation' },
  { key: 'damage_percentage', label: 'Damage %' },
]
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>
    <div v-else-if="scoring" class="rounded-xl border border-border-subtle overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
            <th class="px-4 py-3 text-left">Stat</th>
            <th class="px-4 py-3 text-right">Points</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border-subtle">
          <tr v-for="row in labels" :key="row.key" class="bg-surface">
            <td class="px-4 py-3 text-sm text-foreground">{{ row.label }}</td>
            <td class="px-4 py-3 text-sm text-foreground text-right font-mono">
              {{ scoring[row.key] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
