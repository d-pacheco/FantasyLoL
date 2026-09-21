<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getLeaderboard } from '../../api/fantasyApi'
import { useAuthStore } from '../../stores/auth'
import type { LeaderboardResponse, LeaderboardEntry } from '../../types/fantasy'

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

const members = computed<LeaderboardEntry[]>(() => leaderboard.value?.members ?? [])

// Podium order: 2nd, 1st, 3rd (visual). Only when we have a full podium.
const podium = computed<LeaderboardEntry[]>(() => {
  if (members.value.length < 3) return []
  const byPos = [...members.value].sort((a, b) => a.position - b.position)
  return [byPos[1], byPos[0], byPos[2]]
})

function formatPoints(points: number): string {
  return points.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}

function initials(name: string): string {
  return name.slice(0, 2).toUpperCase()
}

const AVATAR_COLORS = ['#3b82f6', '#f59e0b', '#22c55e', '#a855f7', '#06b6d4', '#ef4444', '#ec4899', '#14b8a6', '#eab308', '#8b5cf6']
function avatarColor(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) % AVATAR_COLORS.length
  return AVATAR_COLORS[h]
}

function rankBadge(position: number): { background: string; color: string } {
  if (position === 1) return { background: '#f59e0b', color: '#0f172a' }
  if (position === 2) return { background: 'rgba(148,163,184,0.35)', color: '#f1f5f9' }
  if (position === 3) return { background: 'rgba(180,120,60,0.35)', color: '#c87941' }
  return { background: 'var(--color-surface-elevated)', color: 'var(--color-foreground-muted)' }
}
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8" data-testid="loading-spinner">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>
    <div v-else-if="leaderboard" class="flex flex-col gap-5">
      <!-- Week context -->
      <div class="text-sm text-foreground-muted">Week {{ leaderboard.current_week }}</div>

      <!-- Podium (top 3) -->
      <div v-if="podium.length === 3" class="grid grid-cols-3 gap-3 sm:gap-4">
        <div
          v-for="entry in podium"
          :key="entry.user_id"
          data-testid="podium-spot"
          class="relative rounded-2xl border p-4 sm:p-5 text-center overflow-hidden"
          :class="entry.position === 1
            ? 'border-accent/40 bg-gradient-to-b from-accent/15 to-surface'
            : 'border-border-subtle bg-surface mt-0 sm:mt-6'"
        >
          <div class="flex flex-col items-center gap-2">
            <!-- rank chip (centered, never clipped) -->
            <div class="flex items-center gap-1.5">
              <svg
                v-if="entry.position === 1"
                class="w-4 h-4 text-accent"
                viewBox="0 0 24 24"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M5 16L3 6l5.5 4L12 4l3.5 6L21 6l-2 10H5zm0 2h14v2H5v-2z" />
              </svg>
              <span
                class="inline-flex items-center justify-center min-w-[2.25rem] h-7 px-2 rounded-full text-sm font-extrabold"
                :style="rankBadge(entry.position)"
              >
                #{{ entry.position }}
              </span>
            </div>

            <div
              class="w-14 h-14 rounded-full flex items-center justify-center text-lg font-bold text-white"
              :style="{ background: avatarColor(entry.username) }"
            >
              {{ initials(entry.username) }}
            </div>
            <p class="font-bold text-sm truncate max-w-full" :class="entry.user_id === auth.userId ? 'text-primary' : 'text-foreground'">
              {{ entry.username }}
            </p>
            <p class="text-xl font-extrabold" :class="entry.position === 1 ? 'text-accent' : 'text-foreground'">
              {{ formatPoints(entry.total_points) }}
            </p>
            <p class="text-[11px] text-foreground-muted -mt-1.5">points</p>
          </div>
        </div>
      </div>

      <!-- Full standings table -->
      <div class="rounded-2xl border border-border-subtle overflow-hidden">
        <div class="grid grid-cols-12 px-5 py-3 text-xs font-semibold text-foreground-muted uppercase tracking-wider border-b border-border-subtle bg-surface">
          <div class="col-span-2">#</div>
          <div class="col-span-7">Manager</div>
          <div class="col-span-3 text-right">Points</div>
        </div>
        <div
          v-for="entry in members"
          :key="entry.user_id"
          data-testid="leaderboard-row"
          class="grid grid-cols-12 items-center px-5 py-3 border-b border-border-subtle last:border-b-0 transition-colors"
          :class="entry.user_id === auth.userId ? 'is-current-user bg-primary/10' : 'bg-surface hover:bg-surface-elevated'"
        >
          <div class="col-span-2">
            <span
              class="inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold"
              :style="rankBadge(entry.position)"
            >
              {{ entry.position }}
            </span>
          </div>
          <div class="col-span-7 flex items-center gap-3 min-w-0">
            <div
              class="w-9 h-9 rounded-full shrink-0 flex items-center justify-center text-xs font-bold text-white"
              :style="{ background: avatarColor(entry.username) }"
            >
              {{ initials(entry.username) }}
            </div>
            <span
              class="text-sm font-medium truncate"
              :class="entry.user_id === auth.userId ? 'text-primary' : 'text-foreground'"
            >
              {{ entry.username }}
              <span v-if="entry.user_id === auth.userId" class="text-xs ml-1 text-foreground-muted">(You)</span>
            </span>
          </div>
          <div class="col-span-3 text-right text-sm font-bold tabular-nums text-foreground">
            {{ formatPoints(entry.total_points) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
