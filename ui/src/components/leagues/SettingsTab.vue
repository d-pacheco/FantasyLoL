<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { FantasyLeagueSettings } from '../../types/fantasy'
import type { League } from '../../types/riot'
import { getRiotLeagues } from '../../api/riotApi'

const props = defineProps<{
  settings: FantasyLeagueSettings | null
  loading: boolean
  error: string
}>()

const riotLeagues = ref<League[]>([])

watch(
  () => props.settings,
  async (settings) => {
    if (settings && settings.available_leagues.length > 0) {
      try {
        const res = await getRiotLeagues()
        riotLeagues.value = res.items
      } catch {
        // fallback to raw IDs if fetch fails
      }
    }
  },
  { immediate: true },
)

const resolvedLeagues = computed(() =>
  (props.settings?.available_leagues ?? []).map(id => {
    const league = riotLeagues.value.find(l => l.id === id)
    return league
      ? { id, name: league.name, image: league.image }
      : { id, name: id, image: null }
  }),
)
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>
    <div v-else-if="settings" class="flex flex-col gap-4">
      <div class="rounded-xl border border-border-subtle overflow-hidden">
        <table class="w-full">
          <tbody class="divide-y divide-border-subtle">
            <tr class="bg-surface">
              <td class="px-4 py-3 text-xs font-medium text-foreground-muted w-40">League Name</td>
              <td class="px-4 py-3 text-sm text-foreground">{{ settings.name }}</td>
            </tr>
            <tr class="bg-surface">
              <td class="px-4 py-3 text-xs font-medium text-foreground-muted">Number of Teams</td>
              <td class="px-4 py-3 text-sm text-foreground">{{ settings.number_of_teams }}</td>
            </tr>
            <tr class="bg-surface">
              <td class="px-4 py-3 text-xs font-medium text-foreground-muted">Available Leagues</td>
              <td class="px-4 py-3 text-sm text-foreground">
                <template v-if="resolvedLeagues.length === 0">—</template>
                <span
                  v-for="league in resolvedLeagues"
                  :key="league.id"
                  class="inline-flex items-center gap-1.5 mr-2 px-2 py-0.5 rounded-md bg-surface-elevated border border-border-subtle"
                >
                  <img
                    v-if="league.image"
                    :src="league.image"
                    :alt="league.name"
                    class="w-4 h-4 object-contain"
                  />
                  <span>{{ league.name }}</span>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
