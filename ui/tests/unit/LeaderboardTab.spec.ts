import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { mockGetLeaderboard } = vi.hoisted(() => ({
  mockGetLeaderboard: vi.fn(),
}))

vi.mock('../../src/api/fantasyApi', () => ({
  getLeaderboard: mockGetLeaderboard,
}))

vi.mock('../../src/stores/auth', () => ({
  useAuthStore: () => ({ userId: 'u2' }),
}))

import LeaderboardTab from '../../src/components/leagues/LeaderboardTab.vue'

const leaderboardData = {
  fantasy_league_id: 'league-1',
  current_week: 5,
  start_week: 1,
  members: [
    { user_id: 'u1', username: 'ProGamer99', total_points: 1247.5, position: 1 },
    { user_id: 'u2', username: 'Summoner42', total_points: 1198.3, position: 2 },
    { user_id: 'u3', username: 'MidLaneMaster', total_points: 1156.8, position: 3 },
    { user_id: 'u4', username: 'JungleDiff', total_points: 1089.2, position: 4 },
  ],
}

const defaultProps = {
  leagueId: 'league-1',
}

describe('LeaderboardTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetLeaderboard.mockResolvedValue(leaderboardData)
  })

  it('displays all members with position, username, and points', async () => {
    const wrapper = mount(LeaderboardTab, { props: defaultProps })
    await flushPromises()

    expect(wrapper.text()).toContain('ProGamer99')
    expect(wrapper.text()).toContain('1,247.5')
    expect(wrapper.text()).toContain('Summoner42')
    expect(wrapper.text()).toContain('MidLaneMaster')
    expect(wrapper.text()).toContain('JungleDiff')
  })

  it('shows current week context', async () => {
    const wrapper = mount(LeaderboardTab, { props: defaultProps })
    await flushPromises()

    expect(wrapper.text()).toContain('Week 5')
  })

  it('highlights the current user row', async () => {
    const wrapper = mount(LeaderboardTab, { props: defaultProps })
    await flushPromises()

    // The current user (u2) row should have a highlight class
    const rows = wrapper.findAll('[data-testid="leaderboard-row"]')
    const currentUserRow = rows.find(r => r.text().includes('Summoner42'))
    expect(currentUserRow?.classes()).toContain('is-current-user')
  })

  it('shows loading spinner while fetching', () => {
    mockGetLeaderboard.mockReturnValue(new Promise(() => {})) // never resolves
    const wrapper = mount(LeaderboardTab, { props: defaultProps })

    expect(wrapper.find('[data-testid="loading-spinner"]').exists()).toBe(true)
  })

  it('shows error state on fetch failure', async () => {
    mockGetLeaderboard.mockRejectedValue(new Error('Network error'))
    const wrapper = mount(LeaderboardTab, { props: defaultProps })
    await flushPromises()

    expect(wrapper.text()).toContain('Unable to load standings')
  })
})
