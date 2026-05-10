<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMatchSchedule, type MatchScheduleResponse } from '../api/riotApi'
import type { Match } from '../types/riot'

const schedule = ref<MatchScheduleResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    schedule.value = await getMatchSchedule()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load schedule'
  } finally {
    loading.value = false
  }
})

function formatLocalTime(utcTime: string): string {
  const date = new Date(utcTime)
  return date.toLocaleString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatScore(match: Match): string {
  if (match.team_1_wins == null && match.team_2_wins == null) {
    return `Bo${match.strategy_count}`
  }
  return `${match.team_1_wins ?? 0} — ${match.team_2_wins ?? 0}`
}
</script>

<template>
  <div class="flex flex-col gap-8">
    <div>
      <h2 class="text-lg font-semibold text-foreground">Matches</h2>
      <p class="mt-1 text-sm text-foreground-muted">Live, upcoming, and recent matches.</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-12 text-danger text-sm">{{ error }}</div>

    <template v-else-if="schedule">
      <!-- Live -->
      <section v-if="schedule.live.length > 0">
        <h3 class="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-live animate-pulse-live" />
          Live
        </h3>
        <div class="flex flex-col gap-3">
          <div v-for="m in schedule.live" :key="m.id" class="rounded-xl p-4 bg-surface border border-border-subtle">
            <div class="grid grid-cols-3 items-center mb-2">
              <span class="text-xs text-foreground-muted uppercase">{{ m.league_slug }}</span>
              <span class="text-xs text-foreground-muted text-center">{{ m.block_name }}</span>
              <span class="text-xs text-foreground-muted text-right">{{ formatLocalTime(m.start_time) }}</span>
            </div>
            <div class="grid grid-cols-[1fr_auto_1fr] items-center">
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <img v-if="m.team_1_image" :src="m.team_1_image" class="w-8 h-8 rounded-full object-cover bg-surface-elevated" />
                <span class="font-semibold text-sm text-foreground truncate">{{ m.team_1_name }}</span>
              </div>
              <div class="text-center px-4 shrink-0">
                <div class="text-lg font-bold tabular-nums text-foreground">{{ formatScore(m) }}</div>
                <div class="text-[11px] font-semibold text-live">LIVE</div>
              </div>
              <div class="flex items-center gap-3 flex-1 min-w-0 justify-end">
                <span class="font-semibold text-sm text-foreground truncate">{{ m.team_2_name }}</span>
                <img v-if="m.team_2_image" :src="m.team_2_image" class="w-8 h-8 rounded-full object-cover bg-surface-elevated" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Upcoming -->
      <section v-if="schedule.upcoming.length > 0">
        <h3 class="text-sm font-semibold text-foreground mb-3">Upcoming</h3>
        <div class="flex flex-col gap-2">
          <div v-for="m in schedule.upcoming" :key="m.id" class="rounded-xl p-4 bg-surface border border-border-subtle">
            <div class="grid grid-cols-3 items-center mb-2">
              <span class="text-xs text-foreground-muted uppercase">{{ m.league_slug }}</span>
              <span class="text-xs text-foreground-muted text-center">{{ m.block_name }}</span>
              <span class="text-xs text-foreground-muted text-right">{{ formatLocalTime(m.start_time) }}</span>
            </div>
            <div class="grid grid-cols-[1fr_auto_1fr] items-center">
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <img v-if="m.team_1_image" :src="m.team_1_image" class="w-8 h-8 rounded-full object-cover bg-surface-elevated" />
                <span class="font-medium text-sm text-foreground truncate">{{ m.team_1_name }}</span>
              </div>
              <span class="text-xs text-foreground-muted px-3">Bo{{ m.strategy_count }}</span>
              <div class="flex items-center gap-3 flex-1 min-w-0 justify-end">
                <span class="font-medium text-sm text-foreground truncate">{{ m.team_2_name }}</span>
                <img v-if="m.team_2_image" :src="m.team_2_image" class="w-8 h-8 rounded-full object-cover bg-surface-elevated" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Recent -->
      <section v-if="schedule.recent.length > 0">
        <h3 class="text-sm font-semibold text-foreground mb-3">Recent Results</h3>
        <div class="flex flex-col gap-2">
          <div v-for="m in schedule.recent" :key="m.id" class="rounded-xl p-4 bg-surface border border-border-subtle">
            <div class="grid grid-cols-3 items-center mb-2">
              <span class="text-xs text-foreground-muted uppercase">{{ m.league_slug }}</span>
              <span class="text-xs text-foreground-muted text-center">{{ m.block_name }}</span>
              <span class="text-xs text-foreground-muted text-right">{{ formatLocalTime(m.start_time) }}</span>
            </div>
            <div class="grid grid-cols-[1fr_auto_1fr] items-center">
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <img v-if="m.team_1_image" :src="m.team_1_image" class="w-8 h-8 rounded-full object-cover bg-surface-elevated" />
                <span class="font-medium text-sm text-foreground truncate" :class="{ 'text-primary': m.winning_team === m.team_1_name }">{{ m.team_1_name }}</span>
              </div>
              <div class="text-center px-3 shrink-0">
                <span class="text-base font-bold tabular-nums text-foreground">{{ formatScore(m) }}</span>
              </div>
              <div class="flex items-center gap-3 flex-1 min-w-0 justify-end">
                <span class="font-medium text-sm text-foreground truncate" :class="{ 'text-primary': m.winning_team === m.team_2_name }">{{ m.team_2_name }}</span>
                <img v-if="m.team_2_image" :src="m.team_2_image" class="w-8 h-8 rounded-full object-cover bg-surface-elevated" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Empty -->
      <div v-if="schedule.live.length === 0 && schedule.upcoming.length === 0 && schedule.recent.length === 0" class="text-center py-12">
        <p class="text-foreground-muted text-sm">No matches scheduled.</p>
      </div>
    </template>
  </div>
</template>
