<script setup lang="ts">
defineProps<{
  leagueName: string
  currentRound: number
  totalRounds: number
  currentPickNumber: number
  totalPicks: number
  currentTurnUsername: string
  isYourTurn: boolean
}>()
</script>

<template>
  <div class="rounded-xl border border-border-subtle overflow-hidden">
    <div class="flex items-center justify-between px-6 py-4 bg-surface">
      <h2 class="text-lg font-semibold text-foreground">DRAFT — {{ leagueName }}</h2>
      <div class="flex items-center gap-4 text-sm text-foreground-muted">
        <span>Round {{ currentRound }} of {{ totalRounds }}</span>
        <span class="text-border-subtle">|</span>
        <span>Pick {{ currentPickNumber }} of {{ totalPicks }}</span>
      </div>
    </div>
    <div
      class="px-6 py-2 text-sm font-medium"
      :class="isYourTurn ? 'bg-primary/10 text-primary' : 'bg-surface-elevated text-foreground-muted'"
    >
      <span v-if="isYourTurn">🟢 Your turn!</span>
      <span v-else>🔵 {{ currentTurnUsername }}'s turn</span>
    </div>
  </div>
</template>
