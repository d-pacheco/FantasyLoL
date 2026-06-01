import { describe, it, expect, vi, beforeEach } from 'vitest'

const { mockMakePick } = vi.hoisted(() => ({ mockMakePick: vi.fn() }))
vi.mock('../../src/api/fantasyApi', () => ({ makePick: mockMakePick }))

import { usePickAction } from '../../src/composables/usePickAction'

describe('usePickAction', () => {
  beforeEach(() => vi.clearAllMocks())

  it('pickDisabled is true when not your turn', () => {
    const { pickDisabled } = usePickAction('l1', { isMyTurn: false })
    expect(pickDisabled.value).toBe(true)
  })

  it('pickDisabled is true while pick is in progress', async () => {
    mockMakePick.mockReturnValue(new Promise(() => {})) // never resolves
    const { pickDisabled, pick } = usePickAction('l1', { isMyTurn: true })
    pick('p1') // don't await — keep it in flight
    expect(pickDisabled.value).toBe(true)
  })

  it('sets pickError and resets pickInProgress on failure', async () => {
    mockMakePick.mockRejectedValue(new Error('already picked'))
    const { pickError, pickInProgress, pick } = usePickAction('l1', { isMyTurn: true })
    await pick('p1')
    expect(pickError.value).toBeTruthy()
    expect(pickInProgress.value).toBe(false)
  })
})
