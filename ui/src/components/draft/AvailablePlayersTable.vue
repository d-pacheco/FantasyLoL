<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ProfessionalPlayer, ProfessionalTeam } from '../../types/riot'

const props = defineProps<{
  players: ProfessionalPlayer[]
  teams: ProfessionalTeam[]
  pickDisabled: boolean
}>()

const emit = defineEmits<{
  pick: [playerId: string]
  pickTeam: [teamId: string]
}>()

type RoleTab = 'all' | 'top' | 'jungle' | 'mid' | 'bottom' | 'support' | 'team'

const tabs: { label: string; value: RoleTab }[] = [
  { label: 'All', value: 'all' },
  { label: 'Top', value: 'top' },
  { label: 'Jungle', value: 'jungle' },
  { label: 'Mid', value: 'mid' },
  { label: 'ADC', value: 'bottom' },
  { label: 'Support', value: 'support' },
  { label: 'Team', value: 'team' },
]

const roleLabels: Record<string, string> = {
  top: 'Top', jungle: 'Jungle', mid: 'Mid', bottom: 'ADC', support: 'Support',
}

const activeTab = ref<RoleTab>('all')
const search = ref('')

const filteredPlayers = computed(() => {
  if (activeTab.value === 'team') return []
  return props.players.filter(p => {
    const matchesRole = activeTab.value === 'all' || p.role === activeTab.value
    const matchesSearch = p.summoner_name.toLowerCase().includes(search.value.toLowerCase())
    return matchesRole && matchesSearch
  })
})

const filteredTeams = computed(() => {
  if (activeTab.value !== 'team') return []
  return props.teams.filter(t =>
    t.name.toLowerCase().includes(search.value.toLowerCase()) ||
    t.code.toLowerCase().includes(search.value.toLowerCase())
  )
})

const showTeams = computed(() => activeTab.value === 'team')
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex items-center justify-between">
      <span class="text-xs font-semibold uppercase tracking-wider text-foreground-muted">Available Players</span>
    </div>

    <!-- Role filter tabs -->
    <div class="flex gap-1 p-1 rounded-lg bg-surface border border-border-subtle w-fit">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
        :class="activeTab === tab.value ? 'bg-primary text-white' : 'text-foreground-muted hover:text-foreground'"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Search -->
    <input
      v-model="search"
      type="text"
      placeholder="Search..."
      class="rounded-lg bg-surface border border-border-subtle px-4 py-2 text-sm text-foreground placeholder:text-foreground-muted focus:outline-none focus:border-primary"
    />

    <!-- Table -->
    <div class="rounded-xl border border-border-subtle overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
            <th class="px-4 py-3 text-left">Name</th>
            <th v-if="!showTeams" class="px-4 py-3 text-left">Role</th>
            <th class="px-4 py-3 text-left">{{ showTeams ? 'Code' : 'Team' }}</th>
            <th class="px-4 py-3 text-left">League</th>
            <th class="px-4 py-3 text-left"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border-subtle">
          <template v-if="!showTeams">
            <tr v-for="player in filteredPlayers" :key="player.id" class="bg-surface hover:bg-surface-elevated transition-colors">
              <td class="px-4 py-3 text-sm font-medium text-foreground">{{ player.summoner_name }}</td>
              <td class="px-4 py-3 text-sm text-foreground-muted">{{ roleLabels[player.role] ?? player.role }}</td>
              <td class="px-4 py-3 text-sm text-foreground-muted">{{ player.team_code ?? '—' }}</td>
              <td class="px-4 py-3 text-sm text-foreground-muted uppercase">{{ player.league_name ?? '—' }}</td>
              <td class="px-4 py-3">
                <button
                  class="px-3 py-1 rounded-md text-xs font-semibold bg-primary/10 text-primary disabled:opacity-40 disabled:cursor-not-allowed"
                  :disabled="pickDisabled"
                  @click="emit('pick', player.id)"
                >
                  Pick
                </button>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="team in filteredTeams" :key="team.id" class="bg-surface hover:bg-surface-elevated transition-colors">
              <td class="px-4 py-3 text-sm font-medium text-foreground">{{ team.name }}</td>
              <td class="px-4 py-3 text-sm text-foreground-muted">{{ team.code }}</td>
              <td class="px-4 py-3 text-sm text-foreground-muted uppercase">{{ team.home_league_name ?? '—' }}</td>
              <td class="px-4 py-3">
                <button
                  class="px-3 py-1 rounded-md text-xs font-semibold bg-primary/10 text-primary disabled:opacity-40 disabled:cursor-not-allowed"
                  :disabled="pickDisabled"
                  @click="emit('pickTeam', team.id)"
                >
                  Pick
                </button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>
