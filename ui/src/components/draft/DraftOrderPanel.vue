<script setup lang="ts">
import { computed } from 'vue'
import type { DraftOrderEntry } from '../../api/fantasyApi'
import type { UserSlots } from '../../types/fantasy'

const props = defineProps<{
  draftOrder: DraftOrderEntry[]
  userSlots: Record<string, UserSlots>
  currentTurnUserId: string | null
}>()

function pickCount(userId: string): number {
  const slots = props.userSlots[userId]
  if (!slots) return 0
  return [slots.top_player_id, slots.jungle_player_id, slots.mid_player_id,
          slots.adc_player_id, slots.support_player_id, slots.team_id]
    .filter(Boolean).length
}
</script>

<template>
  <div class="flex flex-col gap-1">
    <span class="text-xs font-semibold uppercase tracking-wider text-foreground-muted mb-1">Draft Order</span>
    <div
      v-for="entry in draftOrder"
      :key="entry.user_id"
      class="flex items-center justify-between px-3 py-2 rounded-lg border transition-colors"
      :class="entry.user_id === currentTurnUserId
        ? 'bg-primary/10 border-primary text-primary font-semibold'
        : 'bg-surface border-border-subtle text-foreground'"
    >
      <div class="flex items-center gap-2">
        <span class="text-xs text-foreground-muted w-4">{{ entry.position }}.</span>
        <span class="text-sm">{{ entry.username }}</span>
        <span v-if="entry.user_id === currentTurnUserId" class="text-xs">◀</span>
      </div>
      <span class="text-xs text-foreground-muted">{{ pickCount(entry.user_id) }} picks</span>
    </div>
  </div>
</template>
