<script setup lang="ts">
const league = {
  name: 'Worlds Fantasy 2024',
  currentWeek: 8,
  totalWeeks: 12,
  members: 10,
  status: 'active' as const,
  rank: 2,
}

const statusColors: Record<string, { bg: string; text: string }> = {
  active: { bg: 'rgba(34,197,94,0.12)', text: 'var(--color-success)' },
  draft: { bg: 'rgba(245,158,11,0.12)', text: 'var(--color-accent)' },
  completed: { bg: 'rgba(100,116,139,0.12)', text: 'var(--color-foreground-muted)' },
}

const sc = statusColors[league.status]
const progress = (league.currentWeek / league.totalWeeks) * 100
</script>

<template>
  <div class="rounded-xl p-5 flex flex-col gap-4 bg-surface border border-border-subtle">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-semibold text-foreground">My Fantasy League</h2>
      <span
        class="px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wide"
        :style="{ background: sc.bg, color: sc.text }"
      >
        {{ league.status }}
      </span>
    </div>

    <h3 class="text-lg font-bold text-foreground">{{ league.name }}</h3>

    <div class="grid grid-cols-3 gap-3">
      <div class="flex flex-col items-center py-3 rounded-lg bg-surface-elevated">
        <span class="text-2xl font-bold text-primary">{{ league.currentWeek }}</span>
        <span class="text-xs mt-1 text-foreground-muted">Week</span>
      </div>
      <div class="flex flex-col items-center py-3 rounded-lg bg-surface-elevated">
        <span class="text-2xl font-bold text-foreground">{{ league.members }}</span>
        <span class="text-xs mt-1 text-foreground-muted">Members</span>
      </div>
      <div class="flex flex-col items-center py-3 rounded-lg bg-surface-elevated">
        <span class="text-2xl font-bold text-accent">#{{ league.rank }}</span>
        <span class="text-xs mt-1 text-foreground-muted">Your Rank</span>
      </div>
    </div>

    <div>
      <div class="flex justify-between text-xs mb-1.5 text-foreground-muted">
        <span>Season Progress</span>
        <span>{{ league.currentWeek }}/{{ league.totalWeeks }} weeks</span>
      </div>
      <div class="h-2 rounded-full overflow-hidden bg-surface-elevated">
        <div
          class="h-full rounded-full bg-primary transition-all"
          :style="{ width: `${progress}%` }"
        />
      </div>
    </div>
  </div>
</template>
