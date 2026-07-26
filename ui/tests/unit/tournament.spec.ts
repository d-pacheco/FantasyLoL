import { describe, it, expect } from 'vitest'
import { formatTournamentSlug, isActiveOrUpcoming } from '../../src/utils/tournament'

describe('formatTournamentSlug', () => {
  it('splits on underscores, joins with spaces, and uppercases', () => {
    expect(formatTournamentSlug('lcs_split_1_2026')).toBe('LCS SPLIT 1 2026')
  })
})

describe('isActiveOrUpcoming', () => {
  it('returns true when today is within start_date and end_date (active)', () => {
    expect(isActiveOrUpcoming({ start_date: '2020-01-01', end_date: '2999-01-01' })).toBe(true)
  })

  it('returns true when start_date is in the future (upcoming)', () => {
    expect(isActiveOrUpcoming({ start_date: '2999-01-01', end_date: '2999-06-01' })).toBe(true)
  })

  it('returns false when end_date is in the past (completed)', () => {
    expect(isActiveOrUpcoming({ start_date: '2020-01-01', end_date: '2020-06-01' })).toBe(false)
  })
})
