import { describe, it, expect, vi, beforeEach } from 'vitest'

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
}))

vi.mock('../../src/api/client', () => ({
  api: { get: mockGet, post: mockPost, put: vi.fn() },
}))

import { getDraftState, getAvailablePlayers, getAvailableTeams, makePick, startDraft } from '../../src/api/fantasyApi'

describe('getDraftState', () => {
  beforeEach(() => vi.clearAllMocks())

  it('calls GET /fantasy/leagues/{id}/draft/state', async () => {
    mockGet.mockResolvedValue({ data: {} })
    await getDraftState('league-1')
    expect(mockGet).toHaveBeenCalledWith('/fantasy/leagues/league-1/draft/state')
  })
})

describe('getAvailablePlayers', () => {
  beforeEach(() => vi.clearAllMocks())

  it('calls GET /fantasy/leagues/{id}/draft/available-players', async () => {
    mockGet.mockResolvedValue({ data: [] })
    await getAvailablePlayers('league-1')
    expect(mockGet).toHaveBeenCalledWith('/fantasy/leagues/league-1/draft/available-players')
  })
})

describe('getAvailableTeams', () => {
  beforeEach(() => vi.clearAllMocks())

  it('calls GET /fantasy/leagues/{id}/draft/available-teams', async () => {
    mockGet.mockResolvedValue({ data: [] })
    await getAvailableTeams('league-1')
    expect(mockGet).toHaveBeenCalledWith('/fantasy/leagues/league-1/draft/available-teams')
  })
})

describe('makePick', () => {
  beforeEach(() => vi.clearAllMocks())

  it('calls POST /fantasy/leagues/{id}/draft/pick with request body', async () => {
    mockPost.mockResolvedValue({ data: undefined })
    await makePick('league-1', { player_id: 'player-42' })
    expect(mockPost).toHaveBeenCalledWith('/fantasy/leagues/league-1/draft/pick', { player_id: 'player-42' })
  })
})

describe('startDraft', () => {
  beforeEach(() => vi.clearAllMocks())

  it('calls POST /fantasy/leagues/{id}/draft/start', async () => {
    mockPost.mockResolvedValue({ data: undefined })
    await startDraft('league-1')
    expect(mockPost).toHaveBeenCalledWith('/fantasy/leagues/league-1/draft/start')
  })
})
