import { describe, it, expect, vi, beforeEach } from 'vitest'

const { mockGet } = vi.hoisted(() => ({
  mockGet: vi.fn(),
}))

vi.mock('../../src/api/client', () => ({
  api: { get: mockGet },
}))

import { getTournaments } from '../../src/api/riotApi'

describe('getTournaments', () => {
  beforeEach(() => vi.clearAllMocks())

  it('calls GET /riot/tournament', async () => {
    mockGet.mockResolvedValue({ data: { items: [], total: 0, page: 1, size: 50, pages: 0 } })
    await getTournaments()
    expect(mockGet).toHaveBeenCalledWith('/riot/tournament', { params: {} })
  })

  it('passes params through as query params', async () => {
    mockGet.mockResolvedValue({ data: { items: [], total: 0, page: 1, size: 50, pages: 0 } })
    await getTournaments({ size: 100 })
    expect(mockGet).toHaveBeenCalledWith('/riot/tournament', { params: { size: 100 } })
  })
})
