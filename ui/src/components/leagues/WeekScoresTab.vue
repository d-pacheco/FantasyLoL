<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getWeekScores, getLeaderboard } from '../../api/fantasyApi'
import { useAuthStore } from '../../stores/auth'
import type { WeekScoresResponse, RosterSlotScore } from '../../types/fantasy'

const props = defineProps<{
  leagueId: string
  currentWeek: number
  startWeek: number
}>()

const auth = useAuthStore()
const weekData = ref<WeekScoresResponse | null>(null)
const loading = ref(true)
const error = ref('')
const selectedWeek = ref(props.currentWeek)
const expandedSlots = ref<Set<string>>(new Set())
const actualCurrentWeek = ref(props.currentWeek)
const actualStartWeek = ref(props.startWeek)

const roleLabels: Record<string, string> = {
  top: 'Top',
  jungle: 'JG',
  mid: 'Mid',
  adc: 'ADC',
  support: 'Sup',
  team: 'Team',
}

const roleColors: Record<string, string> = {
  top: '#3b82f6',
  jungle: '#22c55e',
  mid: '#a855f7',
  adc: '#f59e0b',
  support: '#06b6d4',
  team: '#6366f1',
}

onMounted(async () => {
  try {
    const leaderboard = await getLeaderboard(props.leagueId)
    actualCurrentWeek.value = leaderboard.current_week
    actualStartWeek.value = leaderboard.start_week
    selectedWeek.value = leaderboard.current_week
  } catch {
    // Fall back to props
  }
})

async function fetchWeek(week: number) {
  loading.value = true
  error.value = ''
  expandedSlots.value.clear()
  try {
    weekData.value = await getWeekScores(props.leagueId, week)
  } catch {
    error.value = 'Unable to load scores.'
  } finally {
    loading.value = false
  }
}

watch(selectedWeek, (week) => fetchWeek(week), { immediate: true })

function prevWeek() {
  if (selectedWeek.value > actualStartWeek.value) {
    selectedWeek.value--
  }
}

function nextWeek() {
  if (selectedWeek.value < actualCurrentWeek.value) {
    selectedWeek.value++
  }
}

function toggleSlot(memberId: string, slot: string) {
  const key = `${memberId}-${slot}`
  if (expandedSlots.value.has(key)) {
    expandedSlots.value.delete(key)
  } else {
    expandedSlots.value.add(key)
  }
}

function isExpanded(memberId: string, slot: string): boolean {
  return expandedSlots.value.has(`${memberId}-${slot}`)
}

function formatPoints(points: number): string {
  return points.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}

function getSlotName(slot: RosterSlotScore): string {
  if (slot.summoner_name) return slot.summoner_name
  if (slot.team_name) return slot.team_name
  return '—'
}
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8" data-testid="loading-spinner">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>
    <div v-else-if="weekData" class="flex flex-col gap-5">
      <!-- Header + week navigation -->
      <div class="flex items-center justify-between gap-4 flex-wrap">
        <h2 class="text-base font-semibold text-foreground">Weekly Scores</h2>
        <div class="flex items-center gap-1 rounded-lg bg-surface border border-border-subtle p-1">
          <button
            data-testid="prev-week"
            class="w-8 h-8 rounded-md flex items-center justify-center text-foreground-muted hover:text-foreground hover:bg-surface-elevated transition-colors disabled:opacity-30 disabled:hover:bg-transparent"
            :disabled="selectedWeek <= actualStartWeek"
            @click="prevWeek"
          >
            ◀
          </button>
          <span class="px-3 text-sm font-semibold text-foreground w-20 text-center">Week {{ selectedWeek }}</span>
          <button
            data-testid="next-week"
            class="w-8 h-8 rounded-md flex items-center justify-center text-foreground-muted hover:text-foreground hover:bg-surface-elevated transition-colors disabled:opacity-30 disabled:hover:bg-transparent"
            :disabled="selectedWeek >= actualCurrentWeek"
            @click="nextWeek"
          >
            ▶
          </button>
        </div>
      </div>

      <!-- Member cards -->
      <div
        v-for="member in weekData.members"
        :key="member.user_id"
        class="rounded-2xl border overflow-hidden"
        :class="member.user_id === auth.userId ? 'border-primary/40 bg-primary/5' : 'border-border-subtle bg-surface'"
      >
        <!-- Member header -->
        <div class="flex items-center justify-between px-5 py-3.5 border-b border-border-subtle">
          <span class="text-sm font-semibold text-foreground">
            {{ member.username }}
            <span v-if="member.user_id === auth.userId" class="text-xs text-foreground-muted ml-1">(You)</span>
          </span>
          <span class="text-sm font-bold tabular-nums text-foreground">
            {{ formatPoints(member.total_points) }} pts
          </span>
        </div>

        <!-- Roster rows -->
        <div class="divide-y divide-border-subtle">
          <div
            v-for="slot in ['top', 'jungle', 'mid', 'adc', 'support', 'team']"
            :key="slot"
          >
            <div
              data-testid="roster-row"
              class="flex items-center gap-3 px-5 py-2.5 cursor-pointer hover:bg-surface-elevated transition-colors"
              @click="toggleSlot(member.user_id, slot)"
            >
              <!-- Role badge -->
              <span
                class="text-[10px] font-bold w-10 text-center py-0.5 rounded-md shrink-0"
                :style="{ background: `${roleColors[slot]}1a`, color: roleColors[slot] }"
              >
                {{ roleLabels[slot] }}
              </span>

              <!-- Player/team name -->
              <span class="flex-1 text-sm text-foreground truncate">
                {{ member.roster[slot] ? getSlotName(member.roster[slot]) : '—' }}
              </span>

              <!-- Points -->
              <span class="text-sm font-semibold tabular-nums text-foreground shrink-0">
                {{ member.roster[slot] ? formatPoints(member.roster[slot].points) : '0.0' }}
              </span>

              <!-- Expand indicator -->
              <svg
                class="w-4 h-4 text-foreground-muted shrink-0 transition-transform"
                :class="isExpanded(member.user_id, slot) ? 'rotate-180' : ''"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                aria-hidden="true"
              >
                <path d="m6 9 6 6 6-6" />
              </svg>
            </div>

            <!-- Expanded breakdown -->
            <div
              v-if="isExpanded(member.user_id, slot) && member.roster[slot] && Object.keys(member.roster[slot].breakdown).length > 0"
              class="px-5 pt-1 pb-3 bg-background/40 border-t border-border-subtle"
            >
              <p class="text-[10px] font-semibold uppercase tracking-wider text-foreground-muted py-2">
                Points Breakdown
              </p>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <div
                  v-for="(entry, category) in member.roster[slot].breakdown"
                  :key="category"
                  class="flex items-center justify-between gap-2 rounded-lg bg-surface border border-border-subtle/60 px-3 py-2"
                >
                  <div class="min-w-0">
                    <p class="text-xs font-medium text-foreground capitalize truncate">{{ category }}</p>
                    <p class="text-[11px] text-foreground-muted tabular-nums">
                      {{ typeof entry === 'object' ? Number(entry.value).toFixed(1) : '' }}
                    </p>
                  </div>
                  <span
                    class="text-xs font-bold tabular-nums shrink-0"
                    :class="(typeof entry === 'object' ? entry.points : Number(entry)) < 0 ? 'text-danger' : 'text-success'"
                  >
                    {{ (typeof entry === 'object' ? entry.points : Number(entry)) > 0 ? '+' : '' }}{{ typeof entry === 'object' ? Number(entry.points).toFixed(1) : Number(entry).toFixed(1) }} pts
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
