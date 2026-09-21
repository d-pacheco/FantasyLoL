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

type Key = keyof FantasyLeagueScoringSettings

const labelFor: Record<string, string> = {
  kills: 'Kills',
  deaths: 'Deaths',
  assists: 'Assists',
  cspm: 'CS Per Minute',
  wards_placed: 'Wards Placed',
  wards_destroyed: 'Wards Destroyed',
  kill_participation: 'Kill Participation',
  damage_percentage: 'Damage %',
  double_kill: 'Double Kill',
  triple_kill: 'Triple Kill',
  quadra_kill: 'Quadra Kill',
  penta_kill: 'Penta Kill',
  match_win: 'Match Win',
  match_sweep: 'Match Sweep',
  dragon: 'Dragon',
  elder_dragon: 'Elder Dragon',
  baron: 'Baron',
  tower: 'Tower',
  inhibitor: 'Inhibitor',
  soul: 'Dragon Soul',
}

// Grouping drives BOTH the read and edit layouts.
// NOTE: 'kills' must remain the first field of the first group — tests target inputs[0].
type Group = { title: string; color: string; keys: Key[] }
const groups: Group[] = [
  { title: 'Combat', color: '#3b82f6', keys: ['kills', 'deaths', 'assists', 'kill_participation', 'damage_percentage'] },
  { title: 'Vision & Farm', color: '#06b6d4', keys: ['cspm', 'wards_placed', 'wards_destroyed'] },
  { title: 'Multikills', color: '#f59e0b', keys: ['double_kill', 'triple_kill', 'quadra_kill', 'penta_kill'] },
  { title: 'Objectives', color: '#22c55e', keys: ['match_win', 'match_sweep', 'dragon', 'elder_dragon', 'baron', 'tower', 'inhibitor', 'soul'] },
]

const allKeys: Key[] = groups.flatMap((g) => g.keys)
const integerFields = new Set<string>(['kills', 'deaths'])

const editing = ref(false)
const saving = ref(false)
const saveError = ref('')
const editValues = reactive<Record<string, number>>({})

function startEditing() {
  if (!props.scoring) return
  for (const key of allKeys) {
    editValues[key] = props.scoring[key] as number
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
      kill_participation: Number(editValues.kill_participation),
      damage_percentage: Number(editValues.damage_percentage),
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
      <!-- Optional edit hint -->
      <p v-if="editing" class="text-xs text-foreground-muted">
        Adjust the points awarded for each stat, then save your changes.
      </p>

      <!-- Grouped category cards (shared layout for read + edit) -->
      <div class="grid sm:grid-cols-2 gap-4">
        <div
          v-for="group in groups"
          :key="group.title"
          class="rounded-2xl border bg-surface p-5 transition-colors"
          :class="editing ? 'border-primary/30' : 'border-border-subtle'"
        >
          <div class="flex items-center gap-2 mb-4">
            <span
              class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold"
              :style="{ background: `${group.color}1a`, color: group.color }"
            >
              {{ group.title.slice(0, 1) }}
            </span>
            <h3 class="text-sm font-semibold text-foreground">{{ group.title }}</h3>
          </div>

          <div class="flex flex-col">
            <div
              v-for="key in group.keys"
              :key="key"
              class="flex items-center justify-between gap-3 py-2 border-b border-border-subtle/50 last:border-0"
            >
              <span class="text-sm text-foreground-muted">{{ labelFor[key] }}</span>

              <!-- Read: static value -->
              <span
                v-if="!editing"
                class="text-sm font-bold tabular-nums"
                :class="(scoring[key] as number) < 0 ? 'text-danger' : 'text-foreground'"
              >
                {{ scoring[key] }}
              </span>

              <!-- Edit: inline number input -->
              <input
                v-else
                v-model.number="editValues[key]"
                type="number"
                :step="integerFields.has(key) ? '1' : 'any'"
                class="w-20 rounded-md bg-surface-elevated border border-border-subtle px-2 py-1 text-sm text-foreground text-right font-mono tabular-nums focus:outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Edit actions -->
      <template v-if="editing">
        <p v-if="saveError" class="text-xs text-danger">{{ saveError }}</p>
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
