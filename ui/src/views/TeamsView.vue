<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getTeams } from '../api/riotApi'
import { usePaginatedQuery } from '../composables/usePaginatedQuery'

const route = useRoute()

const search = ref((route.query.search as string) || '')

const filters = computed(() => ({
  search: search.value || undefined,
  fantasy_available: true,
  active_only: true,
}))

const { data: teams, loading, error, totalPages, currentPage } = usePaginatedQuery(getTeams, filters)

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
      <h2 class="text-lg font-semibold text-foreground">Browse Teams</h2>
      <p class="mt-1 text-sm text-foreground-muted">Search and filter professional teams.</p>
    </div>

    <!-- Search -->
    <div>
      <input
        v-model="search"
        type="text"
        placeholder="Search by team name or code..."
        class="w-full max-w-md rounded-lg bg-surface border border-border-subtle px-4 py-2 text-sm text-foreground placeholder:text-foreground-muted focus:outline-none focus:border-primary"
      />
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
    <div v-else-if="teams.length === 0" class="text-center py-12">
      <p class="text-foreground-muted text-sm">No teams match your search.</p>
    </div>

    <!-- Table -->
    <div v-else class="rounded-xl border border-border-subtle overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
            <th class="px-4 py-3 text-left">Team</th>
            <th class="px-4 py-3 text-left">Code</th>
            <th class="px-4 py-3 text-left">League</th>
            <th class="px-4 py-3 text-left">Region</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border-subtle">
          <tr v-for="team in teams" :key="team.id" class="bg-surface hover:bg-surface-elevated transition-colors">
            <td class="px-4 py-3">
              <div class="flex items-center gap-3">
                <img
                  v-if="team.image"
                  :src="team.image"
                  :alt="team.name"
                  class="w-8 h-8 rounded-full object-cover bg-surface-elevated"
                />
                <div
                  v-else
                  class="w-8 h-8 rounded-full bg-surface-elevated flex items-center justify-center text-xs font-bold text-foreground-muted"
                >
                  {{ team.code }}
                </div>
                <span class="font-medium text-sm text-foreground">{{ team.name }}</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <span class="text-sm font-mono text-foreground-muted">{{ team.code }}</span>
            </td>
            <td class="px-4 py-3">
              <span class="text-sm text-foreground-muted uppercase">{{ team.home_league_name || '—' }}</span>
            </td>
            <td class="px-4 py-3">
              <span class="text-sm text-foreground-muted">{{ team.home_league_region || '—' }}</span>
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
