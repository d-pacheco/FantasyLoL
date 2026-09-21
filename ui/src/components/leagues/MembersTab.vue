<script setup lang="ts">
import { computed } from 'vue'
import type { LeagueMember } from '../../api/fantasyApi'

const props = defineProps<{
  members: LeagueMember[]
  ownerId: string
  loading: boolean
  error: string
}>()

const acceptedCount = computed(() => props.members.filter((m) => m.status === 'accepted').length)

const AVATAR_COLORS = ['#3b82f6', '#f59e0b', '#22c55e', '#a855f7', '#06b6d4', '#ef4444', '#ec4899', '#14b8a6', '#eab308', '#8b5cf6']
function avatarColor(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) % AVATAR_COLORS.length
  return AVATAR_COLORS[h]
}
function initials(name: string): string {
  return name.slice(0, 2).toUpperCase()
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Loading / Error -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>

    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between">
        <h3 class="text-base font-semibold text-foreground">
          Members
          <span class="text-foreground-muted font-normal">({{ acceptedCount }})</span>
        </h3>
      </div>

      <!-- Member cards -->
      <div v-if="members.length > 0" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <div
          v-for="m in members"
          :key="m.user_id"
          data-testid="member-card"
          class="rounded-xl border border-border-subtle bg-surface p-4 flex items-center gap-3"
        >
          <div
            class="w-11 h-11 rounded-full flex items-center justify-center text-sm font-bold text-white shrink-0"
            :style="{ background: avatarColor(m.username) }"
          >
            {{ initials(m.username) }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-foreground truncate flex items-center gap-1.5">
              {{ m.username }}
              <svg
                v-if="m.user_id === ownerId"
                data-testid="owner-badge"
                class="w-3.5 h-3.5 text-accent"
                viewBox="0 0 24 24"
                fill="currentColor"
                aria-label="Owner"
              >
                <title>Owner</title>
                <path d="M5 16L3 6l5.5 4L12 4l3.5 6L21 6l-2 10H5z" />
              </svg>
            </p>
            <p class="text-xs text-foreground-muted">{{ m.user_id === ownerId ? 'Commissioner' : 'Manager' }}</p>
          </div>
          <span
            class="text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wide shrink-0"
            :style="m.status === 'accepted'
              ? { background: 'rgba(34,197,94,0.12)', color: '#22c55e' }
              : { background: 'rgba(245,158,11,0.12)', color: '#f59e0b' }"
          >
            {{ m.status }}
          </span>
        </div>
      </div>
      <div v-else class="rounded-xl border border-border-subtle bg-surface px-4 py-3 text-sm text-foreground-muted">
        No members yet.
      </div>
    </template>
  </div>
</template>
