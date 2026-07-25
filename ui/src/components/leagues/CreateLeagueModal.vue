<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { createLeague } from '../../api/fantasyApi'
import { getRiotLeagues, getTournaments } from '../../api/riotApi'
import { formatTournamentSlug, isActiveOrUpcoming } from '../../utils/tournament'
import type { FantasyLeague } from '../../types/fantasy'
import type { League, Tournament } from '../../types/riot'

const emit = defineEmits<{
  created: [league: FantasyLeague]
  close: []
}>()

const TEAM_COUNTS = [4, 6, 8, 10]

const name = ref('')
const teamCount = ref(6)
const selectedLeagueId = ref('')
const selectedTournamentId = ref('')
const riotLeagues = ref<League[]>([])
const tournaments = ref<Tournament[]>([])
const submitting = ref(false)
const error = ref('')

const isValid = computed(
  () => name.value.trim() !== '' && selectedLeagueId.value !== '' && selectedTournamentId.value !== ''
)

const availableTournaments = computed(() =>
  tournaments.value.filter(
    (t) => t.league_id === selectedLeagueId.value && isActiveOrUpcoming(t)
  )
)

function selectLeague(leagueId: string) {
  selectedLeagueId.value = leagueId
  selectedTournamentId.value = ''
}

onMounted(async () => {
  try {
    const [leaguesRes, tournamentsRes] = await Promise.all([
      getRiotLeagues(true),
      getTournaments({ size: 100 }),
    ])
    riotLeagues.value = leaguesRes.items
    tournaments.value = tournamentsRes.items
  } catch {
    // non-blocking; user will see empty list
  }
})

async function submit() {
  if (!isValid.value) return
  submitting.value = true
  error.value = ''
  try {
    const league = await createLeague({
      name: name.value.trim(),
      number_of_teams: teamCount.value,
      available_leagues: [selectedLeagueId.value],
      tournament_id: selectedTournamentId.value,
    })
    emit('created', league)
  } catch {
    error.value = 'Failed to create league. Please try again.'
  } finally {
    submitting.value = false
  }
}

function onBackdropClick(e: MouseEvent) {
  if (e.target === e.currentTarget) emit('close')
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
    @click="onBackdropClick"
  >
    <div class="w-full max-w-md rounded-xl bg-surface border border-border-subtle p-6 shadow-xl">
      <h2 class="text-lg font-semibold text-foreground mb-5">Create League</h2>

      <div class="flex flex-col gap-4">
        <!-- Name -->
        <div>
          <label class="block text-xs font-medium text-foreground-muted mb-1">League Name</label>
          <input
            v-model="name"
            type="text"
            placeholder="My Fantasy League"
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
              class="px-4 py-1.5 rounded-md text-xs font-medium transition-colors"
              :class="teamCount === n ? 'bg-primary text-white' : 'text-foreground-muted hover:text-foreground'"
              @click="teamCount = n"
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
              class="flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors"
              :class="selectedLeagueId === league.id
                ? 'bg-primary/10 text-primary'
                : 'bg-surface hover:bg-surface-elevated text-foreground'"
              @click="selectLeague(league.id)"
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

        <!-- Tournament -->
        <div v-if="selectedLeagueId">
          <label class="block text-xs font-medium text-foreground-muted mb-1">Select Tournament</label>
          <div class="flex flex-col gap-1 max-h-40 overflow-y-auto rounded-lg border border-border-subtle">
            <button
              v-for="tournament in availableTournaments"
              :key="tournament.id"
              class="flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors"
              :class="selectedTournamentId === tournament.id
                ? 'bg-primary/10 text-primary'
                : 'bg-surface hover:bg-surface-elevated text-foreground'"
              @click="selectedTournamentId = tournament.id"
            >
              <span>{{ formatTournamentSlug(tournament.slug) }}</span>
            </button>
            <p v-if="availableTournaments.length === 0" class="px-4 py-3 text-sm text-foreground-muted">
              No active or upcoming tournaments available for this league.
            </p>
          </div>
        </div>

        <!-- Error -->
        <p v-if="error" class="text-xs text-danger">{{ error }}</p>
      </div>

      <div class="flex justify-end gap-3 mt-6">
        <button
          class="px-4 py-2 rounded-lg text-sm text-foreground-muted hover:text-foreground transition-colors"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          class="px-5 py-2 rounded-lg bg-primary text-white text-sm font-semibold transition-colors hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!isValid || submitting"
          @click="submit"
        >
          {{ submitting ? 'Creating…' : 'Create League' }}
        </button>
      </div>
    </div>
  </div>
</template>
