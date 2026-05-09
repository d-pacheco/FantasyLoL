<script setup lang="ts">
import { TrendingUp, TrendingDown, Minus } from 'lucide-vue-next'
import type { RosterEntry } from '../../types/fantasy'

const roster: RosterEntry[] = [
  { player_id: '1', summoner_name: 'Zeus', role: 'top', team_code: 'T1', points: 87.5, trend: 'up' },
  { player_id: '2', summoner_name: 'Oner', role: 'jungle', team_code: 'T1', points: 92.3, trend: 'up' },
  { player_id: '3', summoner_name: 'Faker', role: 'mid', team_code: 'T1', points: 105.2, trend: 'up' },
  { player_id: '4', summoner_name: 'Gumayusi', role: 'bottom', team_code: 'T1', points: 78.9, trend: 'down' },
  { player_id: '5', summoner_name: 'Keria', role: 'support', team_code: 'T1', points: 68.4, trend: 'neutral' },
]

const total = roster.reduce((s, p) => s + p.points, 0).toFixed(1)

const roleLabels: Record<string, string> = {
  top: 'Top', jungle: 'Jungle', mid: 'Mid', bottom: 'ADC', support: 'Support',
}

const roleColors: Record<string, string> = {
  top: '#3b82f6', jungle: '#22c55e', mid: '#a855f7', bottom: '#f59e0b', support: '#06b6d4',
}

function trendIcon(trend: string) {
  if (trend === 'up') return TrendingUp
  if (trend === 'down') return TrendingDown
  return Minus
}

function trendColor(trend: string) {
  if (trend === 'up') return 'var(--color-success)'
  if (trend === 'down') return 'var(--color-danger)'
  return 'var(--color-foreground-muted)'
}
</script>

<template>
  <div class="rounded-xl p-5 flex flex-col gap-4 lg:col-span-2 bg-surface border border-border-subtle">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-semibold text-foreground">My Team</h2>
      <div class="flex items-center gap-2">
        <span class="text-sm text-foreground-muted">Weekly Total</span>
        <span class="text-xl font-bold text-primary">{{ total }} pts</span>
      </div>
    </div>

    <div class="flex flex-col gap-2">
      <div
        v-for="p in roster"
        :key="p.player_id"
        class="flex items-center gap-4 px-4 py-3 rounded-lg bg-surface-elevated"
      >
        <span
          class="text-xs font-bold w-14 text-center py-1 rounded-md shrink-0"
          :style="{ background: `${roleColors[p.role]}1a`, color: roleColors[p.role] }"
        >
          {{ roleLabels[p.role] }}
        </span>

        <div
          class="w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-[10px] font-bold text-white bg-primary"
        >
          {{ p.team_code }}
        </div>

        <div class="flex-1 min-w-0">
          <p class="font-semibold text-sm text-foreground">{{ p.summoner_name }}</p>
          <p class="text-xs text-foreground-muted">{{ p.team_code }}</p>
        </div>

        <div class="flex items-center gap-1.5 shrink-0">
          <span class="text-base font-bold text-foreground">{{ p.points }}</span>
          <component :is="trendIcon(p.trend)" class="w-4 h-4" :style="{ color: trendColor(p.trend) }" />
        </div>
      </div>
    </div>
  </div>
</template>
