<script setup lang="ts">
import { ref } from 'vue'
import { Trophy } from 'lucide-vue-next'
import LeagueCard from '../components/dashboard/LeagueCard.vue'
import MyTeamCard from '../components/dashboard/MyTeamCard.vue'
import LiveMatchesCard from '../components/dashboard/LiveMatchesCard.vue'
import LeaderboardCard from '../components/dashboard/LeaderboardCard.vue'
import ActivityCard from '../components/dashboard/ActivityCard.vue'

// Mock: set to true to see empty state
const hasLeagues = ref(true)
</script>

<template>
  <div>
    <!-- Page title -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-foreground">Dashboard</h1>
      <p class="text-sm mt-1 text-foreground-muted">Week 8 of 12 — Worlds Fantasy 2024</p>
    </div>

    <!-- Empty state -->
    <div v-if="!hasLeagues" class="flex flex-col items-center justify-center py-20">
      <div class="w-16 h-16 rounded-full bg-surface-elevated flex items-center justify-center mb-4">
        <Trophy class="w-8 h-8 text-foreground-muted" />
      </div>
      <h2 class="text-lg font-semibold text-foreground mb-2">No Fantasy Leagues Yet</h2>
      <p class="text-sm text-foreground-muted mb-6 text-center max-w-md">
        Create a new fantasy league or join an existing one to start competing with friends.
      </p>
      <RouterLink
        to="/leagues"
        class="px-6 py-2.5 rounded-lg bg-primary text-white font-semibold text-sm hover:bg-primary-hover transition-colors"
      >
        Get Started
      </RouterLink>
    </div>

    <!-- Dashboard grid -->
    <div v-else class="grid grid-cols-3 gap-6">
      <LeagueCard />
      <MyTeamCard />
      <LiveMatchesCard />
      <LeaderboardCard />
      <ActivityCard />
    </div>
  </div>
</template>
