<script setup lang="ts">
import type { LiveMatch } from '../../types/fantasy'

const matches: LiveMatch[] = [
  { match_id: '1', team_1_name: 'T1', team_2_name: 'GEN', team_1_score: 2, team_2_score: 1, league_slug: 'worlds', start_time: '2024-11-02T08:00:00Z' },
  { match_id: '2', team_1_name: 'BLG', team_2_name: 'WBG', team_1_score: 1, team_2_score: 1, league_slug: 'worlds', start_time: '2024-11-02T10:00:00Z' },
  { match_id: '3', team_1_name: 'FNC', team_2_name: 'G2', team_1_score: 0, team_2_score: 0, league_slug: 'lec', start_time: '2024-11-02T12:00:00Z' },
]
</script>

<template>
  <div class="rounded-xl p-5 flex flex-col gap-4 bg-surface border border-border-subtle">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-semibold text-foreground flex items-center gap-2">
        <span class="w-2 h-2 rounded-full shrink-0 bg-live animate-pulse-live" />
        Live Matches
      </h2>
      <RouterLink to="/matches" class="text-xs font-medium text-primary">View All</RouterLink>
    </div>

    <div class="flex flex-col gap-3">
      <div
        v-for="m in matches"
        :key="m.match_id"
        class="rounded-lg p-3 bg-surface-elevated"
      >
        <p class="text-xs mb-2 text-foreground-muted">{{ m.league_slug.toUpperCase() }}</p>
        <div class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-2 flex-1 min-w-0">
            <div class="w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-[10px] font-bold text-white bg-primary">
              {{ m.team_1_name.slice(0, 3) }}
            </div>
            <span class="font-semibold text-sm truncate text-foreground">{{ m.team_1_name }}</span>
          </div>

          <div class="text-center shrink-0 px-3">
            <div class="text-lg font-bold tabular-nums text-foreground">
              {{ m.team_1_score }} — {{ m.team_2_score }}
            </div>
            <div class="text-[11px] font-semibold mt-0.5 text-live">LIVE</div>
          </div>

          <div class="flex items-center gap-2 flex-1 min-w-0 justify-end">
            <span class="font-semibold text-sm truncate text-foreground">{{ m.team_2_name }}</span>
            <div class="w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-[10px] font-bold text-white bg-primary">
              {{ m.team_2_name.slice(0, 3) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
