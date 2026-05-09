<script setup lang="ts">
import { ChevronUp, ChevronDown, Minus } from 'lucide-vue-next'
import type { LeaderboardEntry } from '../../types/fantasy'

const entries: LeaderboardEntry[] = [
  { user_id: '1', username: 'ProGamer99', position: 1, points: 1247.5, is_current_user: false },
  { user_id: '2', username: 'Summoner42', position: 2, points: 1198.3, is_current_user: true },
  { user_id: '3', username: 'MidLaneMaster', position: 3, points: 1156.8, is_current_user: false },
  { user_id: '4', username: 'JungleDiff', position: 4, points: 1089.2, is_current_user: false },
  { user_id: '5', username: 'ADCarry1', position: 5, points: 1034.7, is_current_user: false },
]

// Mock trends (not in LeaderboardEntry, just for display)
const trends: Record<string, 'up' | 'down' | 'same'> = {
  '1': 'same', '2': 'up', '3': 'down', '4': 'up', '5': 'down',
}

function trendIcon(userId: string) {
  const t = trends[userId]
  if (t === 'up') return ChevronUp
  if (t === 'down') return ChevronDown
  return Minus
}

function trendColor(userId: string) {
  const t = trends[userId]
  if (t === 'up') return 'var(--color-success)'
  if (t === 'down') return 'var(--color-danger)'
  return 'var(--color-foreground-muted)'
}

function rankStyle(rank: number) {
  if (rank === 1) return { background: 'var(--color-accent)', color: '#000' }
  if (rank === 2) return { background: 'rgba(148,163,184,0.25)', color: 'var(--color-foreground)' }
  if (rank === 3) return { background: 'rgba(180,120,60,0.25)', color: '#c87941' }
  return { background: 'var(--color-surface)', color: 'var(--color-foreground-muted)' }
}
</script>

<template>
  <div class="rounded-xl p-5 flex flex-col gap-4 bg-surface border border-border-subtle">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-semibold text-foreground">Leaderboard</h2>
      <button class="text-xs font-medium text-primary">Full Standings</button>
    </div>

    <div class="flex flex-col gap-2">
      <div
        v-for="e in entries"
        :key="e.user_id"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg"
        :class="e.is_current_user ? 'bg-primary/10 border border-primary/30' : 'bg-surface-elevated border border-transparent'"
      >
        <div
          class="w-7 h-7 rounded-full shrink-0 flex items-center justify-center text-xs font-bold"
          :style="rankStyle(e.position)"
        >
          {{ e.position }}
        </div>

        <div class="flex-1 min-w-0">
          <span
            class="text-sm font-medium truncate block"
            :class="e.is_current_user ? 'text-primary' : 'text-foreground'"
          >
            {{ e.username }}
            <span v-if="e.is_current_user" class="text-xs ml-1 text-foreground-muted">(You)</span>
          </span>
        </div>

        <div class="flex items-center gap-1 shrink-0">
          <span class="text-sm font-bold tabular-nums text-foreground">
            {{ e.points.toLocaleString() }}
          </span>
          <component :is="trendIcon(e.user_id)" class="w-3.5 h-3.5" :style="{ color: trendColor(e.user_id) }" />
        </div>
      </div>
    </div>
  </div>
</template>
