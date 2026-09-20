import { describe, it, expect, vi, beforeEach } from 'vitest'

const { mockGet } = vi.hoisted(() => ({
  mockGet: vi.fn(),
}))

vi.mock('../../src/api/client', () => ({
  api: { get: mockGet },
}))

import {
  getTeamById,
  getTeamRoster,
  getTeamMatchHistory,
  getTeamSummary,
} from '../../src/api/riotApi'

describe('team detail api', () => {
  beforeEach(() => vi.clearAllMocks())

  it('getTeamById calls GET /riot/professional-team/:id', async () => {
    mockGet.mockResolvedValue({ data: { id: '7' } })
    const result = await getTeamById('7')
    expect(mockGet).toHaveBeenCalledWith('/riot/professional-team/7')
    expect(result).toEqual({ id: '7' })
  })

  it('getTeamRoster calls the roster route', async () => {
    mockGet.mockResolvedValue({ data: [] })
    await getTeamRoster('7')
    expect(mockGet).toHaveBeenCalledWith('/riot/professional-team/7/roster')
  })

  it('getTeamMatchHistory calls the match-history route with params', async () => {
    mockGet.mockResolvedValue({ data: { items: [], total: 0, page: 1, size: 20, pages: 0 } })
    await getTeamMatchHistory('7', { page: 2, size: 20 })
    expect(mockGet).toHaveBeenCalledWith('/riot/professional-team/7/match-history', {
      params: { page: 2, size: 20 },
    })
  })

  it('getTeamSummary calls the summary route', async () => {
    mockGet.mockResolvedValue({ data: { team_id: '7', matches_played: 5 } })
    const result = await getTeamSummary('7')
    expect(mockGet).toHaveBeenCalledWith('/riot/professional-team/7/summary')
    expect(result).toEqual({ team_id: '7', matches_played: 5 })
  })
})
