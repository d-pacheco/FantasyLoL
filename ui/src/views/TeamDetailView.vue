<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  getTeamById,
  getTeamRoster,
  getTeamSummary,
  getTeamMatchHistory,
} from '../api/riotApi'
import { usePaginatedQuery } from '../composables/usePaginatedQuery'
import type { ProfessionalTeam, ProfessionalPlayer, TeamSummary } from '../types/riot'

const route = useRoute()
const teamId = route.params.id as string

const roleLabels: Record<string, string> = {
  top: 'Top', jungle: 'Jungle', mid: 'Mid', bottom: 'ADC', support: 'Support', none: '—',
}
const roleColors: Record<string, string> = {
  top: '#3b82f6', jungle: '#22c55e', mid: '#a855f7', bottom: '#f59e0b', support: '#06b6d4', none: '#64748b',
}

const team = ref<ProfessionalTeam | null>(null)
const summary = ref<TeamSummary | null>(null)
const roster = ref<ProfessionalPlayer[]>([])
const headerLoading = ref(true)
const headerError = ref('')

onMounted(async () => {
  try {
    const [t, s, r] = await Promise.all([
      getTeamById(teamId),
      getTeamSummary(teamId),
      getTeamRoster(teamId),
    ])
    team.value = t
    summary.value = s
    roster.value = r
  } catch (e) {
    headerError.value = e instanceof Error ? e.message : 'Failed to load team'
  } finally {
    headerLoading.value = false
  }
})

const noFilters = computed(() => ({}))
const {
  data: matches,
  loading: matchesLoading,
  error: matchesError,
  totalPages,
  currentPage,
} = usePaginatedQuery(
  (params) => getTeamMatchHistory(teamId, params),
  noFilters,
)

const statTiles = computed(() => {
  const s = summary.value
  if (!s) return []
  return [
    { label: 'Matches', value: String(s.matches_played) },
    { label: 'Record', value: `${s.wins}-${s.losses}` },
    { label: 'Win %', value: `${s.win_rate}%` },
    { label: 'Avg Kills', value: String(s.avg_kills) },
    { label: 'Avg Gold', value: `${(s.avg_gold / 1000).toFixed(1)}k` },
    { label: 'Towers', value: String(s.avg_towers) },
    { label: 'Dragons', value: String(s.avg_dragons) },
    { label: 'Barons', value: String(s.avg_barons) },
  ]
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) currentPage.value = page
}

function formatDate(startTime: string | null) {
  return startTime ? startTime.slice(0, 10) : '—'
}

function initials(name: string) {
  return name.slice(0, 2).toUpperCase()
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <RouterLink :to="{ name: 'teams' }" class="text-sm text-foreground-muted hover:text-foreground w-fit">
      ← Back to Teams
    </RouterLink>

    <div v-if="headerLoading" class="flex items-center justify-center py-12">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="headerError" class="text-center py-12 text-danger text-sm">{{ headerError }}</div>

    <template v-else-if="team">
      <!-- Header card -->
      <div class="rounded-xl border border-border-subtle bg-surface p-6">
        <div class="flex items-center gap-5">
          <img
            v-if="team.image"
            :src="team.image"
            :alt="team.name"
            class="w-20 h-20 rounded-xl object-contain bg-surface-elevated p-2"
          />
          <div
            v-else
            class="w-20 h-20 rounded-xl bg-surface-elevated flex items-center justify-center text-xl font-bold text-foreground-muted"
          >
            {{ team.code }}
          </div>
          <div class="flex flex-col gap-1">
            <div class="flex items-center gap-3">
              <h1 class="text-2xl font-bold text-foreground">{{ team.name }}</h1>
              <span class="text-sm font-mono text-foreground-muted">{{ team.code }}</span>
              <span
                class="text-xs font-bold px-2 py-1 rounded-md capitalize"
                :style="{
                  background: `${team.status === 'active' ? '#22c55e' : '#64748b'}1a`,
                  color: team.status === 'active' ? '#22c55e' : '#64748b',
                }"
              >
                {{ team.status }}
              </span>
            </div>
            <p class="text-sm text-foreground">
              <span class="uppercase text-foreground-muted">{{ team.home_league_name || '—' }}</span>
              <span v-if="team.home_league_region" class="text-foreground-muted"> · {{ team.home_league_region }}</span>
            </p>
          </div>
        </div>
      </div>

      <!-- Roster -->
      <div v-if="roster.length" class="flex flex-col gap-4">
        <h2 class="text-lg font-semibold text-foreground">Roster</h2>
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <RouterLink
            v-for="p in roster"
            :key="p.id"
            :to="{ name: 'player-detail', params: { id: p.id } }"
            class="rounded-xl border border-border-subtle bg-surface p-4 flex flex-col items-center gap-2 hover:bg-surface-elevated transition-colors"
          >
            <img
              v-if="p.image"
              :src="p.image"
              :alt="p.summoner_name"
              class="w-14 h-14 rounded-full object-cover bg-surface-elevated"
            />
            <div
              v-else
              class="w-14 h-14 rounded-full bg-surface-elevated flex items-center justify-center text-sm font-bold text-foreground-muted"
            >
              {{ initials(p.summoner_name) }}
            </div>
            <span class="text-sm font-medium text-foreground">{{ p.summoner_name }}</span>
            <span
              class="text-xs font-bold px-2 py-0.5 rounded-md"
              :style="{ background: `${roleColors[p.role]}1a`, color: roleColors[p.role] }"
            >
              {{ roleLabels[p.role] }}
            </span>
          </RouterLink>
        </div>
      </div>

      <!-- Team summary -->
      <div v-if="summary" class="flex flex-col gap-4">
        <h2 class="text-lg font-semibold text-foreground">Team Summary</h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div v-for="tile in statTiles" :key="tile.label" class="rounded-xl border border-border-subtle bg-surface p-4">
            <p class="text-xs text-foreground-muted uppercase tracking-wider">{{ tile.label }}</p>
            <p class="mt-1 text-2xl font-bold text-foreground">{{ tile.value }}</p>
          </div>
        </div>
      </div>

      <!-- Match history -->
      <div class="flex flex-col gap-4">
        <h2 class="text-lg font-semibold text-foreground">Match History</h2>

        <div v-if="matchesLoading" class="flex items-center justify-center py-12">
          <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
        <div v-else-if="matchesError" class="text-center py-12 text-danger text-sm">{{ matchesError }}</div>
        <div v-else-if="matches.length === 0" class="text-center py-12">
          <p class="text-foreground-muted text-sm">No recorded matches for this team.</p>
        </div>

        <div v-else class="rounded-xl border border-border-subtle overflow-x-auto">
          <table class="w-full min-w-[560px]">
            <thead>
              <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
                <th class="px-4 py-3 text-left">Date</th>
                <th class="px-4 py-3 text-left">League</th>
                <th class="px-4 py-3 text-left">Opponent</th>
                <th class="px-4 py-3 text-left">Result</th>
                <th class="px-4 py-3 text-left">Score</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border-subtle">
              <tr v-for="m in matches" :key="m.match_id" class="bg-surface hover:bg-surface-elevated transition-colors text-sm">
                <td class="px-4 py-3 text-foreground-muted whitespace-nowrap">{{ formatDate(m.start_time) }}</td>
                <td class="px-4 py-3 text-foreground-muted uppercase">{{ m.league_slug || '—' }}</td>
                <td class="px-4 py-3 text-foreground">{{ m.opponent_code || '—' }}</td>
                <td class="px-4 py-3">
                  <span
                    v-if="m.win !== null"
                    class="text-xs font-bold px-2 py-0.5 rounded"
                    :style="m.win
                      ? { background: '#22c55e1a', color: '#22c55e' }
                      : { background: '#ef44441a', color: '#ef4444' }"
                  >
                    {{ m.win ? 'W' : 'L' }}
                  </span>
                  <span v-else class="text-foreground-muted">—</span>
                </td>
                <td class="px-4 py-3 text-foreground font-mono">
                  <span v-if="m.team_score !== null && m.opponent_score !== null">{{ m.team_score }}-{{ m.opponent_score }}</span>
                  <span v-else class="text-foreground-muted">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="totalPages > 1" class="flex items-center justify-center gap-1">
          <button
            class="px-3 py-1.5 rounded-md text-xs text-foreground-muted hover:text-foreground disabled:opacity-30"
            :disabled="currentPage <= 1"
            @click="goToPage(currentPage - 1)"
          >
            ← Prev
          </button>
          <button
            v-for="p in visiblePages"
            :key="p"
            class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
            :class="p === currentPage ? 'bg-primary text-white' : 'text-foreground-muted hover:text-foreground'"
            @click="goToPage(p)"
          >
            {{ p }}
          </button>
          <button
            class="px-3 py-1.5 rounded-md text-xs text-foreground-muted hover:text-foreground disabled:opacity-30"
            :disabled="currentPage >= totalPages"
            @click="goToPage(currentPage + 1)"
          >
            Next →
          </button>
        </div>
      </div>
    </template>
  </div>
</template>
