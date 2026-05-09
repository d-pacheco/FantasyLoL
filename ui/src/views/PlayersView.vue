<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getPlayers } from '../api/riotApi'
import { usePaginatedQuery } from '../composables/usePaginatedQuery'

const route = useRoute()

const roles: { label: string; value: string }[] = [
  { label: 'All', value: '' },
  { label: 'Top', value: 'top' },
  { label: 'Jungle', value: 'jungle' },
  { label: 'Mid', value: 'mid' },
  { label: 'ADC', value: 'bottom' },
  { label: 'Support', value: 'support' },
]

const roleLabels: Record<string, string> = {
  top: 'Top', jungle: 'Jungle', mid: 'Mid', bottom: 'ADC', support: 'Support', none: '—',
}

const roleColors: Record<string, string> = {
  top: '#3b82f6', jungle: '#22c55e', mid: '#a855f7', bottom: '#f59e0b', support: '#06b6d4', none: '#64748b',
}

const search = ref((route.query.search as string) || '')
const roleFilter = ref((route.query.role as string) || '')
const teamFilter = ref((route.query.team as string) || '')

const filters = computed(() => ({
  summoner_name: search.value || undefined,
  role: roleFilter.value || undefined,
  team_name: teamFilter.value || undefined,
  fantasy_available: true,
}))

const { data: players, loading, error, totalPages, currentPage } = usePaginatedQuery(getPlayers, filters)

function setRole(value: string) {
  roleFilter.value = value
}

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const visiblePages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <div>
      <h2 class="text-lg font-semibold text-foreground">Browse Players</h2>
      <p class="mt-1 text-sm text-foreground-muted">Search and filter professional players.</p>
    </div>

    <!-- Filters -->
    <div class="flex flex-col gap-4">
      <div class="flex gap-3">
        <input
          v-model="search"
          type="text"
          placeholder="Search by summoner name..."
          class="flex-1 rounded-lg bg-surface border border-border-subtle px-4 py-2 text-sm text-foreground placeholder:text-foreground-muted focus:outline-none focus:border-primary"
        />
        <input
          v-model="teamFilter"
          type="text"
          placeholder="Filter by team..."
          class="w-48 rounded-lg bg-surface border border-border-subtle px-4 py-2 text-sm text-foreground placeholder:text-foreground-muted focus:outline-none focus:border-primary"
        />
      </div>

      <!-- Role segmented control -->
      <div class="flex gap-1 p-1 rounded-lg bg-surface border border-border-subtle w-fit">
        <button
          v-for="r in roles"
          :key="r.value"
          class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
          :class="roleFilter === r.value
            ? 'bg-primary text-white'
            : 'text-foreground-muted hover:text-foreground'"
          @click="setRole(r.value)"
        >
          {{ r.label }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-12 text-danger text-sm">
      {{ error }}
    </div>

    <!-- Empty state -->
    <div v-else-if="players.length === 0" class="text-center py-12">
      <p class="text-foreground-muted text-sm">No players match your filters.</p>
    </div>

    <!-- Table -->
    <div v-else class="rounded-xl border border-border-subtle overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
            <th class="px-4 py-3 text-left">Player</th>
            <th class="px-4 py-3 text-left">Role</th>
            <th class="px-4 py-3 text-left">Team</th>
            <th class="px-4 py-3 text-left">League</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border-subtle">
          <tr v-for="player in players" :key="player.id" class="bg-surface hover:bg-surface-elevated transition-colors">
            <td class="px-4 py-3">
              <div class="flex items-center gap-3">
                <img
                  v-if="player.image"
                  :src="player.image"
                  :alt="player.summoner_name"
                  class="w-8 h-8 rounded-full object-cover bg-surface-elevated"
                />
                <div
                  v-else
                  class="w-8 h-8 rounded-full bg-surface-elevated flex items-center justify-center text-xs font-bold text-foreground-muted"
                >
                  {{ player.summoner_name.slice(0, 2).toUpperCase() }}
                </div>
                <span class="font-medium text-sm text-foreground">{{ player.summoner_name }}</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <span
                class="text-xs font-bold px-2 py-1 rounded-md"
                :style="{ background: `${roleColors[player.role]}1a`, color: roleColors[player.role] }"
              >
                {{ roleLabels[player.role] }}
              </span>
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <span class="text-sm text-foreground">{{ player.team_name || '—' }}</span>
                <span v-if="player.team_code" class="text-xs text-foreground-muted">({{ player.team_code }})</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <span class="text-sm text-foreground-muted uppercase">{{ player.league_name || '—' }}</span>
            </td>
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
        :class="p === currentPage
          ? 'bg-primary text-white'
          : 'text-foreground-muted hover:text-foreground'"
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
