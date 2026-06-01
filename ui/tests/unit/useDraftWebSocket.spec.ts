import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import type { DraftPick, UserSlots, DraftState } from '../../src/types/fantasy'
import type { ProfessionalPlayer, ProfessionalTeam } from '../../src/types/riot'

const { mockGetDraftState, mockGetAvailablePlayers, mockGetAvailableTeams } = vi.hoisted(() => ({
  mockGetDraftState: vi.fn(),
  mockGetAvailablePlayers: vi.fn(),
  mockGetAvailableTeams: vi.fn(),
}))

vi.mock('../../src/api/fantasyApi', () => ({
  getDraftState: mockGetDraftState,
  getAvailablePlayers: mockGetAvailablePlayers,
  getAvailableTeams: mockGetAvailableTeams,
}))

import { handleMessage, refetchIntoState } from '../../src/composables/useDraftWebSocket'

function makeState() {
  return {
    picks: ref<DraftPick[]>([]),
    userSlots: ref<Record<string, UserSlots>>({}),
    availablePlayers: ref<ProfessionalPlayer[]>([]),
    availableTeams: ref<ProfessionalTeam[]>([]),
    currentTurnUserId: ref<string | null>(null),
    isComplete: ref(false),
  }
}

const pick: DraftPick = {
  fantasy_league_id: 'l1',
  pick_number: 1,
  round_number: 1,
  user_id: 'u1',
  player_id: 'p1',
  team_id: null,
}

describe('handleMessage', () => {
  it('pick_made adds pick to picks', () => {
    const state = makeState()
    handleMessage({ event: 'pick_made', pick, next_turn_user_id: 'u2' }, state)
    expect(state.picks.value).toEqual([pick])
  })

  it('pick_made removes player from availablePlayers', () => {
    const state = makeState()
    state.availablePlayers.value = [{ id: 'p1' } as ProfessionalPlayer, { id: 'p2' } as ProfessionalPlayer]
    handleMessage({ event: 'pick_made', pick, next_turn_user_id: 'u2' }, state)
    expect(state.availablePlayers.value.map(p => p.id)).toEqual(['p2'])
  })

  it('pick_made removes team from availableTeams when team pick', () => {
    const teamPick: DraftPick = { ...pick, player_id: null, team_id: 't1' }
    const state = makeState()
    state.availableTeams.value = [{ id: 't1' } as ProfessionalTeam, { id: 't2' } as ProfessionalTeam]
    handleMessage({ event: 'pick_made', pick: teamPick, next_turn_user_id: 'u2' }, state)
    expect(state.availableTeams.value.map(t => t.id)).toEqual(['t2'])
  })

  it('pick_made updates userSlots for the picking user', () => {
    const state = makeState()
    handleMessage({ event: 'pick_made', pick, next_turn_user_id: 'u2' }, state)
    expect(state.userSlots.value['u1']).toBeDefined()
  })

  it('pick_made updates currentTurnUserId', () => {
    const state = makeState()
    handleMessage({ event: 'pick_made', pick, next_turn_user_id: 'u2' }, state)
    expect(state.currentTurnUserId.value).toBe('u2')
  })

  it('draft_completed sets isComplete to true', () => {
    const state = makeState()
    handleMessage({ event: 'draft_completed' }, state)
    expect(state.isComplete.value).toBe(true)
  })
})

describe('refetchIntoState', () => {
  beforeEach(() => vi.clearAllMocks())

  it('rebuilds state from getDraftState, getAvailablePlayers, getAvailableTeams', async () => {
    const draftState: DraftState = {
      fantasy_league_id: 'l1',
      current_round: 2,
      current_pick_number: 5,
      total_picks: 24,
      current_turn_user_id: 'u3',
      picks: [pick],
      user_slots: { u1: { top_player_id: 'p1', jungle_player_id: null, mid_player_id: null, adc_player_id: null, support_player_id: null, team_id: null } },
      is_complete: false,
    }
    mockGetDraftState.mockResolvedValue(draftState)
    mockGetAvailablePlayers.mockResolvedValue([{ id: 'p2' }])
    mockGetAvailableTeams.mockResolvedValue([{ id: 't1' }])

    const state = makeState()
    await refetchIntoState('l1', state)

    expect(state.picks.value).toEqual([pick])
    expect(state.currentTurnUserId.value).toBe('u3')
    expect(state.availablePlayers.value).toEqual([{ id: 'p2' }])
    expect(state.availableTeams.value).toEqual([{ id: 't1' }])
    expect(state.userSlots.value).toEqual(draftState.user_slots)
  })
})
