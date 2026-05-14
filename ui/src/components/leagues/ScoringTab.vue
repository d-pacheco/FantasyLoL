<script setup lang="ts">
import type { FantasyLeagueScoringSettings } from '../../types/fantasy'

defineProps<{
  scoring: FantasyLeagueScoringSettings | null
  loading: boolean
  error: string
}>()

const playerLabels: { key: keyof FantasyLeagueScoringSettings; label: string }[] = [
  { key: 'kills', label: 'Kills' },
  { key: 'deaths', label: 'Deaths' },
  { key: 'assists', label: 'Assists' },
  { key: 'cspm', label: 'CS Per Minute' },
  { key: 'wards_placed', label: 'Wards Placed' },
  { key: 'wards_destroyed', label: 'Wards Destroyed' },
  { key: 'kill_participation', label: 'Kill Participation' },
  { key: 'damage_percentage', label: 'Damage %' },
  { key: 'double_kill', label: 'Double Kill' },
  { key: 'triple_kill', label: 'Triple Kill' },
  { key: 'quadra_kill', label: 'Quadra Kill' },
  { key: 'penta_kill', label: 'Penta Kill' },
]

const teamLabels: { key: keyof FantasyLeagueScoringSettings; label: string }[] = [
  { key: 'match_win', label: 'Match Win' },
  { key: 'match_sweep', label: 'Match Sweep' },
  { key: 'dragon', label: 'Dragon' },
  { key: 'elder_dragon', label: 'Elder Dragon' },
  { key: 'baron', label: 'Baron' },
  { key: 'tower', label: 'Tower' },
  { key: 'inhibitor', label: 'Inhibitor' },
  { key: 'soul', label: 'Dragon Soul' },
]
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>
    <div v-else-if="scoring" class="flex flex-col gap-4">
      <div class="rounded-xl border border-border-subtle overflow-hidden">
        <div class="bg-surface-elevated px-4 py-2 text-xs font-semibold text-foreground-muted uppercase tracking-wider">
          Player Scoring
        </div>
        <table class="w-full">
          <thead>
            <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
              <th class="px-4 py-3 text-left">Stat</th>
              <th class="px-4 py-3 text-right">Points</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border-subtle">
            <tr v-for="row in playerLabels" :key="row.key" class="bg-surface">
              <td class="px-4 py-3 text-sm text-foreground">{{ row.label }}</td>
              <td class="px-4 py-3 text-sm text-foreground text-right font-mono">
                {{ scoring[row.key] }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="rounded-xl border border-border-subtle overflow-hidden">
        <div class="bg-surface-elevated px-4 py-2 text-xs font-semibold text-foreground-muted uppercase tracking-wider">
          Team Scoring
        </div>
        <table class="w-full">
          <thead>
            <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
              <th class="px-4 py-3 text-left">Stat</th>
              <th class="px-4 py-3 text-right">Points</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border-subtle">
            <tr v-for="row in teamLabels" :key="row.key" class="bg-surface">
              <td class="px-4 py-3 text-sm text-foreground">{{ row.label }}</td>
              <td class="px-4 py-3 text-sm text-foreground text-right font-mono">
                {{ scoring[row.key] }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
