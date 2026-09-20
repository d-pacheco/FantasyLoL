<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  getPlayerById,
  getPlayerMatchHistory,
  getPlayerCareerSummary,
} from '../api/riotApi'
import { usePaginatedQuery } from '../composables/usePaginatedQuery'
import type { ProfessionalPlayer, PlayerCareerSummary } from '../types/riot'

const route = useRoute()
const playerId = route.params.id as string

const roleLabels: Record<string, string> = {
  top: 'Top', jungle: 'Jungle', mid: 'Mid', bottom: 'ADC', support: 'Support', none: '—',
}
const roleColors: Record<string, string> = {
  top: '#3b82f6', jungle: '#22c55e', mid: '#a855f7', bottom: '#f59e0b', support: '#06b6d4', none: '#64748b',
}

const player = ref<ProfessionalPlayer | null>(null)
const summary = ref<PlayerCareerSummary | null>(null)
const headerLoading = ref(true)
const headerError = ref('')

onMounted(async () => {
  try {
    const [p, s] = await Promise.all([
      getPlayerById(playerId),
      getPlayerCareerSummary(playerId),
    ])
    player.value = p
    summary.value = s
  } catch (e) {
    headerError.value = e instanceof Error ? e.message : 'Failed to load player'
  } finally {
    headerLoading.value = false
  }
})

// Match history (paginated, server-side) — reuse the shared paginated query composable.
const noFilters = computed(() => ({}))
const {
  data: matches,
  loading: matchesLoading,
  error: matchesError,
  totalPages,
  currentPage,
} = usePaginatedQuery(
  (params) => getPlayerMatchHistory(playerId, params),
  noFilters,
)

const fullName = computed(() => {
  if (!player.value) return ''
  return `${player.value.first_name ?? ''} ${player.value.last_name ?? ''}`.trim()
})

const statTiles = computed(() => {
  const s = summary.value
  if (!s) return []
  return [
    { label: 'Games', value: String(s.games_played) },
    { label: 'KDA', value: s.kda_ratio.toFixed(1), sub: `${s.avg_kills} / ${s.avg_deaths} / ${s.avg_assists}` },
    { label: 'CS / min', value: String(s.cs_per_min), sub: `${s.avg_creep_score} avg` },
    { label: 'Win %', value: `${s.win_rate}%` },
    { label: 'Kill Part.', value: `${s.avg_kill_participation}%` },
    { label: 'Damage %', value: `${s.avg_damage_share}%` },
    { label: 'Gold / min', value: String(s.gold_per_min), sub: `${(s.avg_total_gold / 1000).toFixed(1)}k avg` },
    { label: 'Wards', value: String(s.avg_wards_placed), sub: `${s.avg_wards_destroyed} cleared` },
  ]
})

const multiKillTags = computed(() => {
  const s = summary.value
  if (!s) return []
  return [
    { label: 'Double', count: s.double_kills, color: '#06b6d4' },
    { label: 'Triple', count: s.triple_kills, color: '#a855f7' },
    { label: 'Quadra', count: s.quadra_kills, color: '#f59e0b' },
    { label: 'Penta', count: s.penta_kills, color: '#ef4444' },
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

function sideColor(side: string | null) {
  return side === 'blue' ? '#3b82f6' : side === 'red' ? '#ef4444' : '#64748b'
}

function multiColor(tag: string) {
  return ({ triple: '#a855f7', quadra: '#f59e0b', penta: '#ef4444' } as Record<string, string>)[tag] || '#06b6d4'
}

function formatDate(startTime: string | null) {
  return startTime ? startTime.slice(0, 10) : '—'
}

function formatGold(gold: number) {
  return `${(gold / 1000).toFixed(1)}k`
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <RouterLink :to="{ name: 'players' }" class="text-sm text-foreground-muted hover:text-foreground w-fit">
      ← Back to Players
    </RouterLink>

    <!-- Header loading / error -->
    <div v-if="headerLoading" class="flex items-center justify-center py-12">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="headerError" class="text-center py-12 text-danger text-sm">{{ headerError }}</div>

    <template v-else-if="player">
      <!-- Header card -->
      <div class="rounded-xl border border-border-subtle bg-surface p-6">
        <div class="flex items-center gap-5">
          <img
            v-if="player.image"
            :src="player.image"
            :alt="player.summoner_name"
            class="w-20 h-20 rounded-full object-cover bg-surface-elevated"
          />
          <div
            v-else
            class="w-20 h-20 rounded-full bg-surface-elevated flex items-center justify-center text-xl font-bold text-foreground-muted"
          >
            {{ player.summoner_name.slice(0, 2).toUpperCase() }}
          </div>
          <div class="flex flex-col gap-1">
            <div class="flex items-center gap-3">
              <h1 class="text-2xl font-bold text-foreground">{{ player.summoner_name }}</h1>
              <span
                class="text-xs font-bold px-2 py-1 rounded-md"
                :style="{ background: `${roleColors[player.role]}1a`, color: roleColors[player.role] }"
              >
                {{ roleLabels[player.role] }}
              </span>
            </div>
            <p v-if="fullName" class="text-sm text-foreground-muted">{{ fullName }}</p>
            <p class="text-sm text-foreground">
              {{ player.team_name || '—' }}
              <span v-if="player.team_code" class="text-foreground-muted">({{ player.team_code }})</span>
              <span v-if="player.league_name" class="text-foreground-muted uppercase"> · {{ player.league_name }}</span>
            </p>
          </div>
        </div>
      </div>

      <!-- Career summary -->
      <div v-if="summary" class="flex flex-col gap-4">
        <h2 class="text-lg font-semibold text-foreground">Career Summary</h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div v-for="tile in statTiles" :key="tile.label" class="rounded-xl border border-border-subtle bg-surface p-4">
            <p class="text-xs text-foreground-muted uppercase tracking-wider">{{ tile.label }}</p>
            <p class="mt-1 text-2xl font-bold text-foreground">{{ tile.value }}</p>
            <p v-if="tile.sub" class="text-xs text-foreground-muted">{{ tile.sub }}</p>
          </div>
        </div>
        <div class="flex items-center gap-3 flex-wrap">
          <span class="text-xs text-foreground-muted uppercase tracking-wider">Multi-kills</span>
          <span
            v-for="mk in multiKillTags"
            :key="mk.label"
            class="text-xs font-bold px-2.5 py-1 rounded-md"
            :style="{ background: `${mk.color}1a`, color: mk.color }"
          >
            {{ mk.count }} {{ mk.label }}
          </span>
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
          <p class="text-foreground-muted text-sm">No recorded games for this player.</p>
        </div>

        <div v-else class="rounded-xl border border-border-subtle overflow-x-auto">
          <table class="w-full min-w-[820px]">
            <thead>
              <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
                <th class="px-4 py-3 text-left">Date</th>
                <th class="px-4 py-3 text-left">Opp</th>
                <th class="px-4 py-3 text-left">Side</th>
                <th class="px-4 py-3 text-left">Patch</th>
                <th class="px-4 py-3 text-left">Result</th>
                <th class="px-4 py-3 text-left">K / D / A</th>
                <th class="px-4 py-3 text-left">CS (/m)</th>
                <th class="px-4 py-3 text-left">Gold</th>
                <th class="px-4 py-3 text-left">KP</th>
                <th class="px-4 py-3 text-left">DMG</th>
                <th class="px-4 py-3 text-left">Wards</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border-subtle">
              <tr v-for="m in matches" :key="m.game_id" class="bg-surface hover:bg-surface-elevated transition-colors text-sm">
                <td class="px-4 py-3 text-foreground-muted whitespace-nowrap">{{ formatDate(m.start_time) }}</td>
                <td class="px-4 py-3 text-foreground">{{ m.opponent_code || '—' }}</td>
                <td class="px-4 py-3">
                  <span class="capitalize" :style="{ color: sideColor(m.side) }">{{ m.side || '—' }}</span>
                </td>
                <td class="px-4 py-3 text-foreground-muted">{{ m.patch_version || '—' }}</td>
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
                <td class="px-4 py-3 text-foreground whitespace-nowrap">
                  {{ m.kills }} / {{ m.deaths }} / {{ m.assists }}
                  <span
                    v-for="mk in m.multi_kills"
                    :key="mk"
                    class="ml-1 text-[10px] font-bold px-1.5 py-0.5 rounded uppercase"
                    :style="{ background: `${multiColor(mk)}1a`, color: multiColor(mk) }"
                  >
                    {{ mk }}
                  </span>
                </td>
                <td class="px-4 py-3 text-foreground whitespace-nowrap">
                  {{ m.creep_score }}<span v-if="m.cs_per_min" class="text-foreground-muted"> ({{ m.cs_per_min }})</span>
                </td>
                <td class="px-4 py-3 text-foreground">{{ formatGold(m.total_gold) }}</td>
                <td class="px-4 py-3 text-foreground-muted">{{ m.kill_participation }}%</td>
                <td class="px-4 py-3 text-foreground-muted">{{ m.champion_damage_share }}%</td>
                <td class="px-4 py-3 text-foreground-muted whitespace-nowrap">{{ m.wards_placed }} / {{ m.wards_destroyed }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
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
