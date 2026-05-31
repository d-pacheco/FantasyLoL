import { ref, onMounted, onUnmounted } from 'vue'
import type { Ref } from 'vue'
import type { DraftPick, DraftEvent, UserSlots } from '../types/fantasy'
import type { ProfessionalPlayer, ProfessionalTeam } from '../types/riot'
import { getDraftState, getAvailablePlayers, getAvailableTeams } from '../api/fantasyApi'

export interface DraftWebSocketState {
  picks: Ref<DraftPick[]>
  userSlots: Ref<Record<string, UserSlots>>
  availablePlayers: Ref<ProfessionalPlayer[]>
  availableTeams: Ref<ProfessionalTeam[]>
  currentTurnUserId: Ref<string | null>
  isComplete: Ref<boolean>
}

export function handleMessage(event: DraftEvent, state: DraftWebSocketState): void {
  if (event.event === 'pick_made') {
    const { pick, next_turn_user_id } = event
    state.picks.value.push(pick)
    state.currentTurnUserId.value = next_turn_user_id ?? null
    if (pick.player_id) {
      state.availablePlayers.value = state.availablePlayers.value.filter(p => p.id !== pick.player_id)
      const slots = state.userSlots.value[pick.user_id] ?? {
        top_player_id: null, jungle_player_id: null, mid_player_id: null,
        adc_player_id: null, support_player_id: null, team_id: null,
      }
      state.userSlots.value = { ...state.userSlots.value, [pick.user_id]: slots }
    } else if (pick.team_id) {
      state.availableTeams.value = state.availableTeams.value.filter(t => t.id !== pick.team_id)
      const slots = state.userSlots.value[pick.user_id] ?? {
        top_player_id: null, jungle_player_id: null, mid_player_id: null,
        adc_player_id: null, support_player_id: null, team_id: null,
      }
      state.userSlots.value = { ...state.userSlots.value, [pick.user_id]: { ...slots, team_id: pick.team_id } }
    }
  } else if (event.event === 'draft_completed') {
    state.isComplete.value = true
  }
}

export async function refetchIntoState(leagueId: string, state: DraftWebSocketState): Promise<void> {
  const [draftState, players, teams] = await Promise.all([
    getDraftState(leagueId),
    getAvailablePlayers(leagueId),
    getAvailableTeams(leagueId),
  ])
  state.picks.value = draftState.picks
  state.userSlots.value = draftState.user_slots
  state.currentTurnUserId.value = draftState.current_turn_user_id
  state.isComplete.value = draftState.is_complete
  state.availablePlayers.value = players
  state.availableTeams.value = teams
}

export function useDraftWebSocket(leagueId: string): DraftWebSocketState {
  const state: DraftWebSocketState = {
    picks: ref([]),
    userSlots: ref({}),
    availablePlayers: ref([]),
    availableTeams: ref([]),
    currentTurnUserId: ref(null),
    isComplete: ref(false),
  }

  let ws: WebSocket | null = null
  let backoff = 1000
  let unmounted = false

  function connect() {
    const token = localStorage.getItem('token')
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const url = `${protocol}://${window.location.host}/api/v1/fantasy/leagues/${leagueId}/draft/ws?token=${token}`
    ws = new WebSocket(url)

    ws.onmessage = (msg) => {
      const event: DraftEvent = JSON.parse(msg.data)
      handleMessage(event, state)
    }

    ws.onclose = () => {
      if (unmounted) return
      setTimeout(async () => {
        await refetchIntoState(leagueId, state)
        backoff = Math.min(backoff * 2, 4000)
        connect()
      }, backoff)
    }

    ws.onopen = () => { backoff = 1000 }
  }

  onMounted(connect)
  onUnmounted(() => {
    unmounted = true
    ws?.close()
  })

  return state
}
