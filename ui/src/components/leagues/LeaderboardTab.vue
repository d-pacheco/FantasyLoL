<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getLeaderboard } from '../../api/fantasyApi'
import { useAuthStore } from '../../stores/auth'
import type { LeaderboardResponse } from '../../types/fantasy'

const props = defineProps<{
  leagueId: string
}>()

const auth = useAuthStore()
const leaderboard = ref<LeaderboardResponse | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    leaderboard.value = await getLeaderboard(props.leagueId)
  } catch {
    error.value = 'Unable to load standings.'
  } finally {
    loading.value = false
  }
})

function formatPoints(points: number): string {
  return points.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}

function rankStyle(position: number): { background: string; color: string } {
  if (position === 1) return { background: 'rgba(245,158,11,0.2)', color: '#f59e0b' }
  if (position === 2) return { background: 'rgba(148,163,184,0.2)', color: '#94a3b8' }
  if (position === 3) return { background: 'rgba(180,120,60,0.2)', color: '#c87941' }
  return { background: 'var(--color-surface-elevated)', color: 'var(--color-foreground-muted)' }
}
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8" data-testid="loading-spinner">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>
    <div v-else-if="leaderboard" class="flex flex-col gap-4">
      <!-- Week context -->
      <div class="text-sm text-foreground-muted">
        Week {{ leaderboard.current_week }}
      </div>

      <!-- Standings table -->
      <div class="rounded-xl border border-border-subtle overflow-hidden">
        <div
          v-for="entry in leaderboard.members"
          :key="entry.user_id"
          data-testid="leaderboard-row"
          class="flex items-center gap-4 px-4 py-3 border-b border-border-subtle last:border-b-0 transition-colors"
          :class="entry.user_id === auth.userId ? 'is-current-user bg-primary/10 border-l-2 border-l-primary' : 'bg-surface'"
        >
          <!-- Rank badge -->
          <div
            class="w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-xs font-bold"
            :style="rankStyle(entry.position)"
          >
            {{ entry.position }}
          </div>

          <!-- Username -->
          <div class="flex-1 min-w-0">
            <span
              class="text-sm font-medium truncate block"
              :class="entry.user_id === auth.userId ? 'text-primary' : 'text-foreground'"
            >
              {{ entry.username }}
              <span v-if="entry.user_id === auth.userId" class="text-xs ml-1 text-foreground-muted">(You)</span>
            </span>
          </div>

          <!-- Points -->
          <div class="shrink-0 text-sm font-bold tabular-nums text-foreground">
            {{ formatPoints(entry.total_points) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
