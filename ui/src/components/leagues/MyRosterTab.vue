<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getWeekScores } from '../../api/fantasyApi'
import { getPlayerById, getTeamById } from '../../api/riotApi'
import { useAuthStore } from '../../stores/auth'
import type { WeekScoresResponse, RosterSlotScore } from '../../types/fantasy'
import type { ProfessionalPlayer, ProfessionalTeam } from '../../types/riot'

const props = defineProps<{
  leagueId: string
  currentWeek: number
}>()

const auth = useAuthStore()
const weekData = ref<WeekScoresResponse | null>(null)
const loading = ref(true)
const error = ref('')

const players = ref<Record<string, ProfessionalPlayer>>({})
const teams = ref<Record<string, ProfessionalTeam>>({})

const SLOTS = ['top', 'jungle', 'mid', 'adc', 'support', 'team'] as const

const roleLabels: Record<string, string> = {
  top: 'Top',
  jungle: 'Jungle',
  mid: 'Mid',
  adc: 'ADC',
  support: 'Support',
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

const me = computed(
  () => weekData.value?.members.find((m) => m.user_id === auth.userId) ?? null,
)

const slots = computed(() =>
  SLOTS.map((slot) => ({ slot, data: me.value?.roster[slot] as RosterSlotScore | undefined })),
)

onMounted(async () => {
  try {
    weekData.value = await getWeekScores(props.leagueId, props.currentWeek)
  } catch {
    error.value = 'Unable to load roster.'
    return
  } finally {
    loading.value = false
  }
  await loadIcons()
})

async function loadIcons() {
  const member = me.value
  if (!member) return
  const playerIds = SLOTS.filter((s) => s !== 'team')
    .map((s) => member.roster[s]?.player_id)
    .filter((id): id is string => !!id)
  const teamId = member.roster.team?.team_id

  await Promise.allSettled([
    ...playerIds.map((id) =>
      getPlayerById(id)
        .then((p) => { players.value[id] = p })
        .catch(() => {}),
    ),
    ...(teamId
      ? [getTeamById(teamId).then((t) => { teams.value[teamId] = t }).catch(() => {})]
      : []),
  ])
}

function slotName(data: RosterSlotScore | undefined): string {
  if (!data) return '—'
  return data.summoner_name || data.team_name || '—'
}

function slotImage(slot: string, data: RosterSlotScore | undefined): string | null {
  if (!data) return null
  if (slot === 'team') return data.team_id ? teams.value[data.team_id]?.image || null : null
  return data.player_id ? players.value[data.player_id]?.image || null : null
}

function slotSubLabel(slot: string, data: RosterSlotScore | undefined): string {
  if (slot === 'team') return 'Team'
  if (data?.player_id && players.value[data.player_id]?.team_code) {
    return players.value[data.player_id].team_code as string
  }
  return roleLabels[slot]
}

function initials(name: string): string {
  return name.slice(0, 2).toUpperCase()
}

function formatPoints(points: number): string {
  return points.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8" data-testid="loading-spinner">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>

    <template v-else-if="me">
      <div class="flex flex-col gap-5">
        <!-- Header -->
        <div class="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h2 class="text-base font-semibold text-foreground">My Roster</h2>
            <p class="text-sm text-foreground-muted mt-0.5">Week {{ weekData?.week }}</p>
          </div>
          <span class="text-sm text-foreground-muted">
            Weekly total
            <span class="text-primary font-bold ml-1">{{ formatPoints(me.total_points) }} pts</span>
          </span>
        </div>

        <!-- Roster slots -->
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="{ slot, data } in slots"
            :key="slot"
            data-testid="roster-slot"
            class="rounded-2xl border border-border-subtle bg-surface p-5 hover:border-primary/40 transition-colors"
          >
            <span
              class="text-[11px] font-bold px-2 py-1 rounded"
              :style="{ background: `${roleColors[slot]}1a`, color: roleColors[slot] }"
            >
              {{ roleLabels[slot] }}
            </span>

            <div class="flex items-center gap-3 mt-4">
              <div
                class="w-12 h-12 rounded-xl overflow-hidden shrink-0 flex items-center justify-center bg-surface-elevated"
              >
                <img
                  v-if="slotImage(slot, data)"
                  :src="slotImage(slot, data) as string"
                  :alt="slotName(data)"
                  class="w-full h-full object-contain"
                />
                <span
                  v-else
                  class="w-full h-full flex items-center justify-center text-sm font-bold text-white"
                  :style="{ background: data ? roleColors[slot] : '#334155' }"
                >
                  {{ data ? initials(slotName(data)) : '—' }}
                </span>
              </div>
              <div class="min-w-0">
                <p class="font-bold text-foreground truncate">{{ slotName(data) }}</p>
                <p class="text-xs text-foreground-muted">{{ slotSubLabel(slot, data) }}</p>
              </div>
            </div>

            <div class="flex items-end justify-between mt-4 pt-4 border-t border-border-subtle">
              <div>
                <p class="text-2xl font-extrabold text-primary">{{ data ? formatPoints(data.points) : '0.0' }}</p>
                <p class="text-[11px] text-foreground-muted">week pts</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-16 text-center">
      <div class="w-14 h-14 rounded-full bg-surface-elevated flex items-center justify-center mb-3">
        <svg class="w-6 h-6 text-foreground-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      </div>
      <h3 class="text-sm font-semibold text-foreground">No roster yet</h3>
      <p class="text-sm text-foreground-muted mt-1 max-w-sm">
        Your roster isn't set for this week.
      </p>
    </div>
  </div>
</template>
