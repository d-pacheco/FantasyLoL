import { describe, it, expect, vi, beforeEach } from 'vitest'

const { mockGet } = vi.hoisted(() => ({
  mockGet: vi.fn(),
}))

vi.mock('../../src/api/client', () => ({
  api: { get: mockGet },
}))

import {
  getPlayerById,
  getPlayerMatchHistory,
  getPlayerCareerSummary,
} from '../../src/api/riotApi'

describe('player detail api', () => {
  beforeEach(() => vi.clearAllMocks())

  it('getPlayerById calls GET /riot/professional-player/:id', async () => {
    mockGet.mockResolvedValue({ data: { id: '42' } })
    const result = await getPlayerById('42')
    expect(mockGet).toHaveBeenCalledWith('/riot/professional-player/42')
    expect(result).toEqual({ id: '42' })
  })

  it('getPlayerMatchHistory calls the match-history route with params', async () => {
    mockGet.mockResolvedValue({ data: { items: [], total: 0, page: 1, size: 20, pages: 0 } })
    await getPlayerMatchHistory('42', { page: 2, size: 20 })
    expect(mockGet).toHaveBeenCalledWith('/riot/professional-player/42/match-history', {
      params: { page: 2, size: 20 },
    })
  })

  it('getPlayerCareerSummary calls the summary route', async () => {
    mockGet.mockResolvedValue({ data: { player_id: '42', games_played: 3 } })
    const result = await getPlayerCareerSummary('42')
    expect(mockGet).toHaveBeenCalledWith('/riot/professional-player/42/summary')
    expect(result).toEqual({ player_id: '42', games_played: 3 })
  })
})
