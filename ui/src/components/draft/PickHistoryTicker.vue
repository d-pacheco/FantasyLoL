<script setup lang="ts">
import { computed } from 'vue'
import type { DraftPick } from '../../types/fantasy'
import type { ProfessionalPlayer, ProfessionalTeam } from '../../types/riot'
import type { DraftOrderEntry } from '../../api/fantasyApi'

const props = defineProps<{
  picks: DraftPick[]
  players: ProfessionalPlayer[]
  teams: ProfessionalTeam[]
  draftOrder: DraftOrderEntry[]
}>()

function resolveName(pick: DraftPick): string {
  if (pick.player_id) return props.players.find(p => p.id === pick.player_id)?.summoner_name ?? pick.player_id
  if (pick.team_id) return props.teams.find(t => t.id === pick.team_id)?.name ?? pick.team_id
  return '?'
}

function resolveUsername(userId: string): string {
  return props.draftOrder.find(e => e.user_id === userId)?.username ?? userId
}

// Most recent first
const orderedPicks = computed(() => [...props.picks].reverse())
</script>

<template>
  <div class="flex flex-col gap-2">
    <span class="text-xs font-semibold uppercase tracking-wider text-foreground-muted">Pick History</span>
    <div class="flex gap-2 overflow-x-auto pb-1">
      <div
        v-for="pick in orderedPicks"
        :key="pick.pick_number"
        class="flex-shrink-0 flex flex-col gap-0.5 px-3 py-2 rounded-lg bg-surface border border-border-subtle min-w-[120px]"
      >
        <span class="text-xs text-foreground-muted">#{{ pick.pick_number }} · {{ resolveUsername(pick.user_id) }}</span>
        <span class="text-sm font-medium text-foreground">{{ resolveName(pick) }}</span>
      </div>
      <div v-if="picks.length === 0" class="text-sm text-foreground-muted italic">No picks yet.</div>
    </div>
  </div>
</template>
