<script setup lang="ts">
import { computed } from 'vue'
import type { FantasyLeague } from '../../types/fantasy'
import type { LeagueMember } from '../../api/fantasyApi'

interface HeroStats {
  rank: number
  points: number
  pointsBehind: number
  week: number
}

const props = defineProps<{
  league: FantasyLeague | null
  members: LeagueMember[]
  isOwner: boolean
  currentUserId: string
  starting: boolean
  leaving: boolean
  startError: string
  stats: HeroStats | null
}>()

const emit = defineEmits<{
  'start-draft': []
  leave: []
  'join-draft': []
  invite: []
}>()

const AVATAR_COLORS = [
  '#3b82f6', '#f59e0b', '#22c55e', '#a855f7', '#06b6d4',
  '#ef4444', '#ec4899', '#14b8a6', '#eab308', '#8b5cf6',
]

const acceptedMembers = computed(() =>
  props.members.filter((m) => m.status === 'accepted'),
)
const acceptedCount = computed(() => acceptedMembers.value.length)
const capacity = computed(() => props.league?.number_of_teams ?? 0)
const isFull = computed(() => capacity.value > 0 && acceptedCount.value >= capacity.value)
const spotsRemaining = computed(() => Math.max(0, capacity.value - acceptedCount.value))

const statusColors: Record<string, string> = {
  'pre-draft': '#f59e0b',
  draft: '#3b82f6',
  active: '#22c55e',
  completed: '#64748b',
}
const statusColor = computed(() => statusColors[props.league?.status ?? ''] ?? '#64748b')
const statusPill = computed(() => ({
  background: `${statusColor.value}26`,
  color: statusColor.value,
}))

function initials(name: string): string {
  return name.slice(0, 2).toUpperCase()
}
function avatarColor(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) % AVATAR_COLORS.length
  return AVATAR_COLORS[h]
}

function formatPoints(points: number): string {
  return points.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}
</script>

<template>
  <section class="relative overflow-hidden rounded-2xl border border-border-subtle">
    <!-- gradient banner -->
    <div class="absolute inset-0 bg-gradient-to-br from-primary/25 via-surface to-accent/10" />
    <div class="absolute -right-16 -top-16 w-64 h-64 rounded-full bg-primary/20 blur-3xl" />
    <div class="absolute -left-10 -bottom-20 w-64 h-64 rounded-full bg-accent/10 blur-3xl" />

    <div class="relative p-6 sm:p-7">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div class="flex items-start gap-4">
          <!-- crest -->
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-primary-hover flex items-center justify-center shadow-lg shadow-primary/30 shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>
          </div>

          <div>
            <div class="flex items-center gap-3 flex-wrap">
              <h1 class="text-2xl font-extrabold tracking-tight text-foreground">
                {{ league?.name ?? 'League' }}
              </h1>
              <span
                v-if="league"
                class="px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider capitalize"
                :style="statusPill"
              >
                <span
                  class="inline-block w-1.5 h-1.5 rounded-full mr-1 align-middle"
                  :class="league.status === 'active' ? 'animate-pulse-live' : ''"
                  :style="{ background: statusColor }"
                />
                {{ league.status }}
              </span>
            </div>

            <!-- member avatars + count -->
            <div class="flex items-center gap-2 mt-3">
              <div class="flex -space-x-2">
                <div
                  v-for="m in acceptedMembers.slice(0, 6)"
                  :key="m.user_id"
                  class="w-7 h-7 rounded-full ring-2 ring-surface flex items-center justify-center text-[10px] font-bold text-white"
                  :style="{ background: avatarColor(m.username) }"
                  :title="m.username"
                >
                  {{ initials(m.username) }}
                </div>
              </div>
              <span data-testid="member-count" class="text-xs text-foreground-muted">
                {{ acceptedCount }}/{{ capacity }} managers
              </span>
            </div>
          </div>
        </div>

        <!-- contextual actions -->
        <div class="flex flex-col items-end gap-2">
          <!-- Join Draft: anyone, during draft -->
          <button
            v-if="league?.status === 'draft'"
            class="px-5 py-2.5 rounded-xl text-sm font-semibold bg-primary text-white hover:bg-primary-hover transition-colors shadow-lg shadow-primary/25"
            @click="emit('join-draft')"
          >
            Join Draft
          </button>

          <!-- Start Draft: owner, pre-draft -->
          <template v-else-if="isOwner && league?.status === 'pre-draft'">
            <button
              class="px-5 py-2.5 rounded-xl text-sm font-semibold transition-colors"
              :class="isFull
                ? 'bg-primary text-white hover:bg-primary-hover shadow-lg shadow-primary/25'
                : 'bg-surface/60 border border-border-subtle text-foreground-muted cursor-not-allowed'"
              :disabled="!isFull || starting"
              @click="emit('start-draft')"
            >
              {{ starting ? 'Starting…' : 'Start Draft' }}
            </button>
            <button
              class="px-4 py-2 rounded-xl text-sm font-medium bg-surface/60 backdrop-blur border border-border-subtle text-foreground-muted hover:text-foreground transition-colors"
              @click="emit('invite')"
            >
              Invite friends
            </button>
            <p v-if="startError" class="text-xs text-danger">{{ startError }}</p>
            <p v-if="!isFull" class="text-xs text-foreground-muted">
              Need {{ spotsRemaining }} more member{{ spotsRemaining === 1 ? '' : 's' }} to start
            </p>
          </template>

          <!-- Leave: non-owner, pre-draft -->
          <button
            v-else-if="!isOwner && league?.status === 'pre-draft'"
            class="px-4 py-2 rounded-xl text-sm font-medium bg-surface/60 backdrop-blur border border-border-subtle text-foreground-muted hover:text-foreground transition-colors"
            :disabled="leaving"
            @click="emit('leave')"
          >
            {{ leaving ? 'Leaving…' : 'Leave League' }}
          </button>
        </div>
      </div>

      <!-- stat tiles: only when the season is under way (active/completed) -->
      <div
        v-if="stats"
        data-testid="hero-stats"
        class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6"
      >
        <div class="rounded-xl bg-surface/70 backdrop-blur border border-border-subtle p-4">
          <p class="text-xs text-foreground-muted">Your Rank</p>
          <p class="text-2xl font-extrabold text-accent mt-1">
            #{{ stats.rank }}<span class="text-sm text-foreground-muted font-semibold"> / {{ acceptedCount }}</span>
          </p>
        </div>
        <div class="rounded-xl bg-surface/70 backdrop-blur border border-border-subtle p-4">
          <p class="text-xs text-foreground-muted">Your Points</p>
          <p class="text-2xl font-extrabold text-foreground mt-1">
            {{ formatPoints(stats.points) }}<span class="text-sm text-foreground-muted font-semibold"> pts</span>
          </p>
        </div>
        <div class="rounded-xl bg-surface/70 backdrop-blur border border-border-subtle p-4">
          <p class="text-xs text-foreground-muted">Current Week</p>
          <p class="text-2xl font-extrabold text-foreground mt-1">{{ stats.week }}</p>
        </div>
        <div class="rounded-xl bg-surface/70 backdrop-blur border border-border-subtle p-4">
          <p class="text-xs text-foreground-muted">
            {{ stats.rank === 1 ? 'Lead over #2' : 'Behind #1' }}
          </p>
          <p class="text-2xl font-extrabold mt-1" :class="stats.rank === 1 ? 'text-success' : 'text-danger'">
            {{ formatPoints(stats.pointsBehind) }}<span class="text-sm text-foreground-muted font-semibold"> pts</span>
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
