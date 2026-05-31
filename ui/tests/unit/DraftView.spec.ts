import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'

const {
  mockGetLeagueById, mockGetDraftState, mockGetAvailablePlayers,
  mockGetAvailableTeams, mockGetDraftOrder, wsState,
} = vi.hoisted(() => {
  const { ref } = require('vue')
  return {
    mockGetLeagueById: vi.fn(),
    mockGetDraftState: vi.fn(),
    mockGetAvailablePlayers: vi.fn(),
    mockGetAvailableTeams: vi.fn(),
    mockGetDraftOrder: vi.fn(),
    wsState: {
      picks: ref([]),
      userSlots: ref({}),
      availablePlayers: ref([] as unknown[]),
      availableTeams: ref([]),
      currentTurnUserId: ref(null as string | null),
      isComplete: ref(false),
    },
  }
})

vi.mock('../../src/api/fantasyApi', () => ({
  getLeagueById: mockGetLeagueById,
  getDraftState: mockGetDraftState,
  getAvailablePlayers: mockGetAvailablePlayers,
  getAvailableTeams: mockGetAvailableTeams,
  getDraftOrder: mockGetDraftOrder,
  makePick: vi.fn(),
}))

vi.mock('../../src/composables/useDraftWebSocket', () => ({
  useDraftWebSocket: () => wsState,
}))

vi.mock('../../src/stores/auth', () => ({
  useAuthStore: () => ({ userId: 'u1' }),
}))

import DraftView from '../../src/views/DraftView.vue'

const faker = {
  id: 'p1', summoner_name: 'Faker', role: 'mid', team_id: 't1',
  team_name: 'T1', team_code: 'T1', image: '', first_name: '', last_name: '', league_name: 'LCK',
}

function makeRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/leagues/:id/draft', name: 'league-draft', component: DraftView },
      { path: '/leagues/:id', name: 'league-detail', component: { template: '<div>detail</div>' } },
    ],
  })
  router.push('/leagues/l1/draft')
  return router
}

const baseDraftState = {
  fantasy_league_id: 'l1', current_round: 1, current_pick_number: 1,
  total_picks: 24, current_turn_user_id: 'u2', picks: [], user_slots: {}, is_complete: false,
}

describe('DraftView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    wsState.picks.value = []
    wsState.userSlots.value = {}
    wsState.availablePlayers.value = []
    wsState.availableTeams.value = []
    wsState.currentTurnUserId.value = null
    wsState.isComplete.value = false
    mockGetAvailablePlayers.mockResolvedValue([])
    mockGetAvailableTeams.mockResolvedValue([])
    mockGetDraftOrder.mockResolvedValue([])
  })

  it('redirects to league-detail when status is PRE_DRAFT', async () => {
    mockGetLeagueById.mockResolvedValue({ id: 'l1', name: 'Test', status: 'pre-draft' })
    const router = makeRouter()
    await router.isReady()
    mount(DraftView, { global: { plugins: [router] } })
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('league-detail')
  })

  it('renders pick buttons disabled in read-only mode when status is ACTIVE', async () => {
    mockGetLeagueById.mockResolvedValue({ id: 'l1', name: 'Test', status: 'active' })
    mockGetDraftState.mockResolvedValue({ ...baseDraftState, picks: [], user_slots: {}, is_complete: true })
    mockGetAvailablePlayers.mockResolvedValue([faker])
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(DraftView, { global: { plugins: [router] } })
    await flushPromises()
    const pickButtons = wrapper.findAll('button').filter(b => b.text() === 'Pick')
    expect(pickButtons.length).toBeGreaterThan(0)
    pickButtons.forEach(b => expect((b.element as HTMLButtonElement).disabled).toBe(true))
  })

  it('renders pick buttons enabled when status is DRAFT and it is the user\'s turn', async () => {
    mockGetLeagueById.mockResolvedValue({ id: 'l1', name: 'Test', status: 'draft' })
    wsState.availablePlayers.value = [faker]
    wsState.currentTurnUserId.value = 'u1'
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(DraftView, { global: { plugins: [router] } })
    await flushPromises()
    const pickButtons = wrapper.findAll('button').filter(b => b.text() === 'Pick')
    expect(pickButtons.length).toBeGreaterThan(0)
    pickButtons.forEach(b => expect((b.element as HTMLButtonElement).disabled).toBe(false))
  })
})
