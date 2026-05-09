<script setup lang="ts">
import { Zap, ArrowRightLeft, UserPlus, PlusCircle } from 'lucide-vue-next'
import type { ActivityEvent } from '../../types/fantasy'
import type { Component } from 'vue'

const activities: (ActivityEvent & { icon: Component; style: { bg: string; color: string } })[] = [
  { id: '1', type: 'score', description: 'Faker scored 32.5 pts in T1 vs GEN', timestamp: '2m ago', icon: Zap, style: { bg: 'rgba(59,130,246,0.12)', color: 'var(--color-primary)' } },
  { id: '2', type: 'trade', description: 'Trade accepted: Chovy for ShowMaker', timestamp: '15m ago', icon: ArrowRightLeft, style: { bg: 'rgba(245,158,11,0.12)', color: 'var(--color-accent)' } },
  { id: '3', type: 'pickup', description: 'MidLaneMaster drafted Ruler', timestamp: '1h ago', icon: UserPlus, style: { bg: 'rgba(34,197,94,0.12)', color: 'var(--color-success)' } },
  { id: '4', type: 'score', description: 'Zeus earned First Blood bonus (+5 pts)', timestamp: '2h ago', icon: Zap, style: { bg: 'rgba(59,130,246,0.12)', color: 'var(--color-primary)' } },
  { id: '5', type: 'pickup', description: 'Kiin added from waivers', timestamp: '3h ago', icon: PlusCircle, style: { bg: 'rgba(100,116,139,0.12)', color: 'var(--color-foreground-muted)' } },
]
</script>

<template>
  <div class="rounded-xl p-5 flex flex-col gap-4 bg-surface border border-border-subtle">
    <h2 class="text-base font-semibold text-foreground">Recent Activity</h2>

    <div class="flex flex-col gap-3">
      <div v-for="a in activities" :key="a.id" class="flex items-start gap-3">
        <div
          class="w-8 h-8 rounded-lg shrink-0 flex items-center justify-center"
          :style="{ background: a.style.bg, color: a.style.color }"
        >
          <component :is="a.icon" class="w-4 h-4" />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm leading-snug text-foreground">{{ a.description }}</p>
          <p class="text-xs mt-0.5 text-foreground-muted">{{ a.timestamp }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
