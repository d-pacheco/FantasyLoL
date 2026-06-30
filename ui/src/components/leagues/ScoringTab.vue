<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FantasyLeagueScoringSettings } from '../../types/fantasy'
import { updateLeagueScoringSettings } from '../../api/fantasyApi'

const props = defineProps<{
  scoring: FantasyLeagueScoringSettings | null
  loading: boolean
  error: string
  editable: boolean
  leagueId: string
}>()

const emit = defineEmits<{
  updated: [scoring: FantasyLeagueScoringSettings]
}>()

const playerLabels: { key: keyof FantasyLeagueScoringSettings; label: string }[] = [
  { key: 'kills', label: 'Kills' },
  { key: 'deaths', label: 'Deaths' },
  { key: 'assists', label: 'Assists' },
  { key: 'cspm', label: 'CS Per Minute' },
  { key: 'wards_placed', label: 'Wards Placed' },
  { key: 'wards_destroyed', label: 'Wards Destroyed' },
  { key: 'kill_participation', label: 'Kill Participation' },
  { key: 'damage_percentage', label: 'Damage %' },
  { key: 'double_kill', label: 'Double Kill' },
  { key: 'triple_kill', label: 'Triple Kill' },
  { key: 'quadra_kill', label: 'Quadra Kill' },
  { key: 'penta_kill', label: 'Penta Kill' },
]

const teamLabels: { key: keyof FantasyLeagueScoringSettings; label: string }[] = [
  { key: 'match_win', label: 'Match Win' },
  { key: 'match_sweep', label: 'Match Sweep' },
  { key: 'dragon', label: 'Dragon' },
  { key: 'elder_dragon', label: 'Elder Dragon' },
  { key: 'baron', label: 'Baron' },
  { key: 'tower', label: 'Tower' },
  { key: 'inhibitor', label: 'Inhibitor' },
  { key: 'soul', label: 'Dragon Soul' },
]

const allFields = [...playerLabels, ...teamLabels]

const integerFields = new Set<string>(['kills', 'deaths', 'kill_participation', 'damage_percentage'])

const editing = ref(false)
const saving = ref(false)
const saveError = ref('')
const editValues = reactive<Record<string, number>>({})

function startEditing() {
  if (!props.scoring) return
  for (const field of allFields) {
    editValues[field.key] = props.scoring[field.key] as number
  }
  saveError.value = ''
  editing.value = true
}

function cancelEditing() {
  editing.value = false
  saveError.value = ''
}

async function save() {
  saving.value = true
  saveError.value = ''
  try {
    const payload: FantasyLeagueScoringSettings = {
      fantasy_league_id: null,
      kills: Math.round(Number(editValues.kills)),
      deaths: Math.round(Number(editValues.deaths)),
      assists: Number(editValues.assists),
      cspm: Number(editValues.cspm),
      wards_placed: Number(editValues.wards_placed),
      wards_destroyed: Number(editValues.wards_destroyed),
      kill_participation: Math.round(Number(editValues.kill_participation)),
      damage_percentage: Math.round(Number(editValues.damage_percentage)),
      double_kill: Number(editValues.double_kill),
      triple_kill: Number(editValues.triple_kill),
      quadra_kill: Number(editValues.quadra_kill),
      penta_kill: Number(editValues.penta_kill),
      match_win: Number(editValues.match_win),
      match_sweep: Number(editValues.match_sweep),
      dragon: Number(editValues.dragon),
      elder_dragon: Number(editValues.elder_dragon),
      baron: Number(editValues.baron),
      tower: Number(editValues.tower),
      inhibitor: Number(editValues.inhibitor),
      soul: Number(editValues.soul),
    }
    const updated = await updateLeagueScoringSettings(props.leagueId, payload)
    emit('updated', updated)
    editing.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      saveError.value = axiosErr.response?.data?.detail ?? 'Failed to save scoring settings.'
    } else {
      saveError.value = 'Failed to save scoring settings.'
    }
  } finally {
    saving.value = false
  }
}

defineExpose({ startEditing })
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>
    <div v-else-if="scoring" class="flex flex-col gap-4">
      <!-- Read-only view -->
      <template v-if="!editing">
        <div class="rounded-xl border border-border-subtle overflow-hidden">
          <div class="bg-surface-elevated px-4 py-2 text-xs font-semibold text-foreground-muted uppercase tracking-wider">
            Player Scoring
          </div>
          <table class="w-full">
            <thead>
              <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
                <th class="px-4 py-3 text-left">Stat</th>
                <th class="px-4 py-3 text-right">Points</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border-subtle">
              <tr v-for="row in playerLabels" :key="row.key" class="bg-surface">
                <td class="px-4 py-3 text-sm text-foreground">{{ row.label }}</td>
                <td class="px-4 py-3 text-sm text-foreground text-right font-mono">
                  {{ scoring[row.key] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="rounded-xl border border-border-subtle overflow-hidden">
          <div class="bg-surface-elevated px-4 py-2 text-xs font-semibold text-foreground-muted uppercase tracking-wider">
            Team Scoring
          </div>
          <table class="w-full">
            <thead>
              <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
                <th class="px-4 py-3 text-left">Stat</th>
                <th class="px-4 py-3 text-right">Points</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border-subtle">
              <tr v-for="row in teamLabels" :key="row.key" class="bg-surface">
                <td class="px-4 py-3 text-sm text-foreground">{{ row.label }}</td>
                <td class="px-4 py-3 text-sm text-foreground text-right font-mono">
                  {{ scoring[row.key] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <!-- Edit form -->
      <template v-else>
        <div class="rounded-xl border border-border-subtle overflow-hidden">
          <div class="bg-surface-elevated px-4 py-2 text-xs font-semibold text-foreground-muted uppercase tracking-wider">
            Player Scoring
          </div>
          <table class="w-full">
            <thead>
              <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
                <th class="px-4 py-3 text-left">Stat</th>
                <th class="px-4 py-3 text-right">Points</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border-subtle">
              <tr v-for="row in playerLabels" :key="row.key" class="bg-surface">
                <td class="px-4 py-3 text-sm text-foreground">{{ row.label }}</td>
                <td class="px-4 py-3 text-right">
                  <input
                    v-model.number="editValues[row.key]"
                    type="number"
                    :step="integerFields.has(row.key) ? '1' : 'any'"
                    class="w-20 rounded-md bg-surface-elevated border border-border-subtle px-2 py-1 text-sm text-foreground text-right font-mono focus:outline-none focus:border-primary"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="rounded-xl border border-border-subtle overflow-hidden">
          <div class="bg-surface-elevated px-4 py-2 text-xs font-semibold text-foreground-muted uppercase tracking-wider">
            Team Scoring
          </div>
          <table class="w-full">
            <thead>
              <tr class="bg-surface-elevated text-xs text-foreground-muted uppercase tracking-wider">
                <th class="px-4 py-3 text-left">Stat</th>
                <th class="px-4 py-3 text-right">Points</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border-subtle">
              <tr v-for="row in teamLabels" :key="row.key" class="bg-surface">
                <td class="px-4 py-3 text-sm text-foreground">{{ row.label }}</td>
                <td class="px-4 py-3 text-right">
                  <input
                    v-model.number="editValues[row.key]"
                    type="number"
                    :step="integerFields.has(row.key) ? '1' : 'any'"
                    class="w-20 rounded-md bg-surface-elevated border border-border-subtle px-2 py-1 text-sm text-foreground text-right font-mono focus:outline-none focus:border-primary"
                  />
                </td>
              </tr>
            </tbody>
          </table>
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
            :disabled="saving"
            @click="save"
          >
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>
