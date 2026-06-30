<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { FantasyLeagueSettings } from '../../types/fantasy'
import type { League } from '../../types/riot'
import { getRiotLeagues } from '../../api/riotApi'
import { updateLeagueSettings } from '../../api/fantasyApi'

const TEAM_COUNTS = [4, 6, 8, 10]

const props = defineProps<{
  settings: FantasyLeagueSettings | null
  loading: boolean
  error: string
  editable: boolean
  leagueId: string
}>()

const emit = defineEmits<{
  updated: [settings: FantasyLeagueSettings]
}>()

const riotLeagues = ref<League[]>([])
const editing = ref(false)
const saving = ref(false)
const saveError = ref('')

// Edit form state
const editName = ref('')
const editTeamCount = ref(6)
const editLeagueId = ref('')

watch(
  () => props.settings,
  async (settings) => {
    if (settings) {
      try {
        const res = await getRiotLeagues(true)
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

function startEditing() {
  if (!props.settings) return
  editName.value = props.settings.name
  editTeamCount.value = props.settings.number_of_teams
  editLeagueId.value = props.settings.available_leagues[0] ?? ''
  saveError.value = ''
  editing.value = true
}

defineExpose({ startEditing })

function cancelEditing() {
  editing.value = false
  saveError.value = ''
}

async function save() {
  saving.value = true
  saveError.value = ''
  try {
    const updated = await updateLeagueSettings(props.leagueId, {
      name: editName.value.trim(),
      number_of_teams: editTeamCount.value,
      available_leagues: editLeagueId.value ? [editLeagueId.value] : [],
    })
    emit('updated', updated)
    editing.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      saveError.value = axiosErr.response?.data?.detail ?? 'Failed to save settings.'
    } else {
      saveError.value = 'Failed to save settings.'
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>
    <div v-else-if="settings" class="flex flex-col gap-4">
      <!-- Read-only view -->
      <div v-if="!editing" class="rounded-xl border border-border-subtle overflow-hidden">
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

      <!-- Edit form -->
      <div v-else class="flex flex-col gap-4">
        <!-- Name -->
        <div>
          <label class="block text-xs font-medium text-foreground-muted mb-1">League Name</label>
          <input
            v-model="editName"
            type="text"
            class="w-full rounded-lg bg-surface-elevated border border-border-subtle px-4 py-2 text-sm text-foreground placeholder:text-foreground-muted focus:outline-none focus:border-primary"
          />
        </div>

        <!-- Team Count -->
        <div>
          <label class="block text-xs font-medium text-foreground-muted mb-1">Number of Teams</label>
          <div class="flex gap-1 p-1 rounded-lg bg-surface-elevated border border-border-subtle w-fit">
            <button
              v-for="n in TEAM_COUNTS"
              :key="n"
              type="button"
              class="px-4 py-1.5 rounded-md text-xs font-medium transition-colors"
              :class="editTeamCount === n ? 'bg-primary text-white' : 'text-foreground-muted hover:text-foreground'"
              @click="editTeamCount = n"
            >
              {{ n }}
            </button>
          </div>
        </div>

        <!-- Riot League -->
        <div>
          <label class="block text-xs font-medium text-foreground-muted mb-1">Select League</label>
          <div class="flex flex-col gap-1 max-h-40 overflow-y-auto rounded-lg border border-border-subtle">
            <button
              v-for="league in riotLeagues"
              :key="league.id"
              type="button"
              class="flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors"
              :class="editLeagueId === league.id
                ? 'bg-primary/10 text-primary'
                : 'bg-surface hover:bg-surface-elevated text-foreground'"
              @click="editLeagueId = league.id"
            >
              <img v-if="league.image" :src="league.image" :alt="league.name" class="w-5 h-5 object-contain" />
              <span>{{ league.name }}</span>
              <span class="ml-auto text-xs text-foreground-muted">{{ league.region }}</span>
            </button>
            <p v-if="riotLeagues.length === 0" class="px-4 py-3 text-sm text-foreground-muted">
              No leagues available.
            </p>
          </div>
        </div>

        <!-- Error -->
        <p v-if="saveError" class="text-xs text-danger">{{ saveError }}</p>

        <!-- Actions -->
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 rounded-lg text-sm text-foreground-muted hover:text-foreground transition-colors"
            @click="cancelEditing"
          >
            Cancel
          </button>
          <button
            type="button"
            class="px-5 py-2 rounded-lg bg-primary text-white text-sm font-semibold transition-colors hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="saving || editName.trim() === ''"
            @click="save"
          >
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
