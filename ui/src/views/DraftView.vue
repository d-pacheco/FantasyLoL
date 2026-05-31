<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getLeagueById, getDraftState, getAvailablePlayers, getAvailableTeams, getDraftOrder } from '../api/fantasyApi'
import { useDraftWebSocket } from '../composables/useDraftWebSocket'
import { usePickAction } from '../composables/usePickAction'
import type { FantasyLeague } from '../types/fantasy'
import type { DraftOrderEntry } from '../api/fantasyApi'
import type { ProfessionalPlayer, ProfessionalTeam } from '../types/riot'
import DraftHeader from '../components/draft/DraftHeader.vue'
import AvailablePlayersTable from '../components/draft/AvailablePlayersTable.vue'
import RosterPanel from '../components/draft/RosterPanel.vue'
import DraftOrderPanel from '../components/draft/DraftOrderPanel.vue'
import PickHistoryTicker from '../components/draft/PickHistoryTicker.vue'
import DraftCompleteModal from '../components/draft/DraftCompleteModal.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const leagueId = route.params.id as string

const league = ref<FantasyLeague | null>(null)
const draftOrder = ref<DraftOrderEntry[]>([])
const allPlayers = ref<ProfessionalPlayer[]>([])
const allTeams = ref<ProfessionalTeam[]>([])
const readOnlyPlayers = ref<ProfessionalPlayer[]>([])
const readOnlyTeams = ref<ProfessionalTeam[]>([])
const isReadOnly = ref(false)

const ws = useDraftWebSocket(leagueId)

// For read-only mode, use REST-fetched lists; for live mode, use WS reactive lists
const availablePlayers = computed(() => isReadOnly.value ? readOnlyPlayers.value : ws.availablePlayers.value)
const availableTeams = computed(() => isReadOnly.value ? readOnlyTeams.value : ws.availableTeams.value)

const isMyTurn = computed(() =>
  !isReadOnly.value && ws.currentTurnUserId.value === auth.userId
)

const { pickDisabled, pickError, pick, pickTeam } = usePickAction(leagueId, { isMyTurn })

const mySlots = computed(() => ws.userSlots.value[auth.userId ?? ''] ?? {
  top_player_id: null, jungle_player_id: null, mid_player_id: null,
  adc_player_id: null, support_player_id: null, team_id: null,
})

const currentTurnUsername = computed(() => {
  const id = ws.currentTurnUserId.value
  return draftOrder.value.find(e => e.user_id === id)?.username ?? '...'
})

// Derive round/pick from picks count + total
const totalRounds = computed(() => draftOrder.value.length || 6)
const currentRound = computed(() => ws.picks.value.length > 0
  ? Math.ceil((ws.picks.value.length + 1) / draftOrder.value.length)
  : 1
)

onMounted(async () => {
  const [leagueData, orderData] = await Promise.all([
    getLeagueById(leagueId),
    getDraftOrder(leagueId),
  ])
  league.value = leagueData
  draftOrder.value = orderData

  if (leagueData.status === 'pre-draft') {
    router.replace({ name: 'league-detail', params: { id: leagueId } })
    return
  }

  // Load full lists once — used for name resolution in roster + history
  const [players, teams, state] = await Promise.all([
    getAvailablePlayers(leagueId),
    getAvailableTeams(leagueId),
    getDraftState(leagueId),
  ])
  allPlayers.value = players
  allTeams.value = teams

  // Seed WS state with initial REST data (WS only pushes deltas after this)
  ws.picks.value = state.picks
  ws.userSlots.value = state.user_slots
  ws.currentTurnUserId.value = state.current_turn_user_id
  ws.isComplete.value = state.is_complete
  ws.availablePlayers.value = players
  ws.availableTeams.value = teams

  if (leagueData.status === 'active' || leagueData.status === 'completed') {
    isReadOnly.value = true
    readOnlyPlayers.value = players
    readOnlyTeams.value = teams
  }
})

function onGoToLeague() {
  router.push({ name: 'league-detail', params: { id: leagueId } })
}
</script>

<template>
  <div class="flex flex-col gap-4 h-full">
    <DraftHeader
      v-if="league"
      :league-name="league.name"
      :current-round="currentRound"
      :total-rounds="totalRounds"
      :current-pick-number="ws.picks.value.length + 1"
      :total-picks="totalRounds * 6"
      :current-turn-username="currentTurnUsername"
      :is-your-turn="isMyTurn"
    />

    <div class="flex gap-4 flex-1 min-h-0">
      <!-- Left: available players -->
      <div class="flex-1 min-w-0">
        <AvailablePlayersTable
          :players="availablePlayers"
          :teams="availableTeams"
          :pick-disabled="pickDisabled || isReadOnly"
          @pick="pick"
          @pick-team="pickTeam"
        />
        <p v-if="pickError" class="mt-2 text-xs text-danger">{{ pickError }}</p>
      </div>

      <!-- Right: roster + draft order -->
      <div class="w-56 flex-shrink-0 flex flex-col gap-4">
        <RosterPanel :slots="mySlots" :players="allPlayers" :teams="allTeams" />
        <DraftOrderPanel
          :draft-order="draftOrder"
          :user-slots="ws.userSlots.value"
          :current-turn-user-id="ws.currentTurnUserId.value"
        />
      </div>
    </div>

    <!-- Bottom: pick history -->
    <PickHistoryTicker
      :picks="ws.picks.value"
      :players="allPlayers"
      :teams="allTeams"
      :draft-order="draftOrder"
    />

    <DraftCompleteModal :show="ws.isComplete.value" @go-to-league="onGoToLeague" />
  </div>
</template>
