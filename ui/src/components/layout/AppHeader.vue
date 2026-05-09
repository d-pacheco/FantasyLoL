<script setup lang="ts">
import { ref } from 'vue'
import { Trophy, ChevronDown, Bell } from 'lucide-vue-next'
import { useFantasyLeagueStore } from '../../stores/fantasyLeague'

const store = useFantasyLeagueStore()
const open = ref(false)

// Mock leagues until real API integration
const mockLeagues = [
  { id: '1', name: 'Worlds Fantasy 2024' },
  { id: '2', name: 'LCS Spring Split' },
  { id: '3', name: 'LEC Champions' },
]

const selectedName = ref(
  mockLeagues.find((l) => l.id === store.selectedLeagueId)?.name ?? mockLeagues[0].name
)

function selectLeague(league: { id: string; name: string }) {
  store.selectLeague(league.id)
  selectedName.value = league.name
  open.value = false
}
</script>

<template>
  <header
    class="h-16 flex items-center justify-between px-6 sticky top-0 z-30 bg-surface border-b border-border-subtle"
  >
    <!-- League selector -->
    <div class="relative">
      <button
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-surface-elevated border border-border-subtle text-foreground"
        @click="open = !open"
      >
        <Trophy class="w-4 h-4 text-accent" />
        <span>{{ selectedName }}</span>
        <ChevronDown class="w-4 h-4 text-foreground-muted" />
      </button>

      <div
        v-if="open"
        class="absolute top-full left-0 mt-2 w-56 rounded-lg py-1 z-50 shadow-2xl bg-surface-elevated border border-border-subtle"
      >
        <button
          v-for="league in mockLeagues"
          :key="league.id"
          class="w-full text-left px-4 py-2.5 text-sm transition-colors hover:bg-primary/8"
          :class="league.id === store.selectedLeagueId ? 'text-primary' : 'text-foreground'"
          @click="selectLeague(league)"
        >
          {{ league.name }}
        </button>
      </div>
    </div>

    <!-- Right side -->
    <div class="flex items-center gap-3">
      <button class="relative p-2 rounded-lg text-foreground-muted hover:bg-surface-elevated">
        <Bell class="w-5 h-5" />
        <span
          class="absolute top-1 right-1 w-4 h-4 rounded-full text-[10px] font-bold text-white flex items-center justify-center bg-danger"
        >
          3
        </span>
      </button>
    </div>
  </header>
</template>
