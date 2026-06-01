<script setup lang="ts">
import { computed } from 'vue'
import type { UserSlots } from '../../types/fantasy'
import type { ProfessionalPlayer, ProfessionalTeam } from '../../types/riot'

const props = defineProps<{
  slots: UserSlots
  players: ProfessionalPlayer[]
  teams: ProfessionalTeam[]
}>()

function playerName(id: string | null): string | null {
  if (!id) return null
  return props.players.find(p => p.id === id)?.summoner_name ?? id
}

function teamName(id: string | null): string | null {
  if (!id) return null
  return props.teams.find(t => t.id === id)?.name ?? id
}

const rosterSlots = computed(() => [
  { label: 'TOP',  name: playerName(props.slots.top_player_id) },
  { label: 'JGL',  name: playerName(props.slots.jungle_player_id) },
  { label: 'MID',  name: playerName(props.slots.mid_player_id) },
  { label: 'ADC',  name: playerName(props.slots.adc_player_id) },
  { label: 'SUP',  name: playerName(props.slots.support_player_id) },
  { label: 'TEAM', name: teamName(props.slots.team_id) },
])
</script>

<template>
  <div class="flex flex-col gap-1">
    <span class="text-xs font-semibold uppercase tracking-wider text-foreground-muted mb-1">Your Roster</span>
    <div
      v-for="slot in rosterSlots"
      :key="slot.label"
      class="flex items-center gap-3 px-3 py-2 rounded-lg bg-surface border border-border-subtle"
    >
      <span class="text-xs font-bold text-foreground-muted w-10">{{ slot.label }}</span>
      <span v-if="slot.name" class="text-sm font-medium text-foreground">{{ slot.name }}</span>
      <span v-else class="text-sm text-foreground-muted italic">empty</span>
    </div>
  </div>
</template>
