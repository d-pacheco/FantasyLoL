import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { mockGetWeekScores } = vi.hoisted(() => ({
  mockGetWeekScores: vi.fn(),
}))

vi.mock('../../src/api/fantasyApi', () => ({
  getWeekScores: mockGetWeekScores,
  getLeaderboard: vi.fn().mockResolvedValue({ current_week: 5, start_week: 1, members: [] }),
}))

vi.mock('../../src/stores/auth', () => ({
  useAuthStore: () => ({ userId: 'u1' }),
}))

import WeekScoresTab from '../../src/components/leagues/WeekScoresTab.vue'

const weekScoresData = {
  fantasy_league_id: 'league-1',
  week: 3,
  members: [
    {
      user_id: 'u1',
      username: 'nightlen',
      total_points: 142.5,
      roster: {
        top: { player_id: 'p1', summoner_name: 'Zeus', points: 28.3, breakdown: { kills: { value: 8, points: 18 }, deaths: { value: 2, points: -2 }, assists: { value: 10, points: 10 } } },
        jungle: { player_id: 'p2', summoner_name: 'Oner', points: 31.1, breakdown: { kills: { value: 7, points: 15 }, deaths: { value: 3, points: -3 }, assists: { value: 14, points: 14 } } },
        mid: { player_id: 'p3', summoner_name: 'Faker', points: 42.7, breakdown: { kills: { value: 10, points: 24 }, deaths: { value: 1, points: -1 }, assists: { value: 12, points: 12 } } },
        adc: { player_id: 'p4', summoner_name: 'Gumayusi', points: 22.4, breakdown: { kills: { value: 6, points: 12 }, deaths: { value: 4, points: -4 }, assists: { value: 8, points: 8 } } },
        support: { player_id: 'p5', summoner_name: 'Keria', points: 12.0, breakdown: { kills: { value: 2, points: 3 }, deaths: { value: 2, points: -2 }, assists: { value: 20, points: 20 } } },
        team: { team_id: 't1', team_name: 'T1', points: 6.0, breakdown: { match_win: { value: 1, points: 5 }, dragon: { value: 2, points: 2 }, baron: { value: 1, points: 2 } } },
      },
    },
    {
      user_id: 'u2',
      username: 'test123',
      total_points: 98.2,
      roster: {
        top: { player_id: null, summoner_name: null, points: 0, breakdown: {} },
        jungle: { player_id: 'p6', summoner_name: 'Canyon', points: 35.2, breakdown: { kills: { value: 9, points: 20 }, deaths: { value: 2, points: -2 }, assists: { value: 12, points: 12 } } },
        mid: { player_id: 'p7', summoner_name: 'Chovy', points: 38.0, breakdown: { kills: { value: 10, points: 22 }, deaths: { value: 1, points: -1 }, assists: { value: 10, points: 10 } } },
        adc: { player_id: 'p8', summoner_name: 'Ruler', points: 25.0, breakdown: { kills: { value: 7, points: 14 }, deaths: { value: 3, points: -3 }, assists: { value: 9, points: 9 } } },
        support: { player_id: null, summoner_name: null, points: 0, breakdown: {} },
        team: { team_id: null, team_name: null, points: 0, breakdown: {} },
      },
    },
  ],
}

const defaultProps = {
  leagueId: 'league-1',
  currentWeek: 5,
  startWeek: 1,
}

describe('WeekScoresTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetWeekScores.mockResolvedValue(weekScoresData)
  })

  it('displays member rosters with player names and points', async () => {
    const wrapper = mount(WeekScoresTab, { props: defaultProps })
    await flushPromises()

    expect(wrapper.text()).toContain('nightlen')
    expect(wrapper.text()).toContain('142.5')
    expect(wrapper.text()).toContain('Faker')
    expect(wrapper.text()).toContain('42.7')
    expect(wrapper.text()).toContain('T1')
  })

  it('shows week navigation with current week as default', async () => {
    const wrapper = mount(WeekScoresTab, { props: defaultProps })
    await flushPromises()

    // Should show week number and navigation arrows
    expect(wrapper.text()).toContain('Week')
    // Should have fetched with currentWeek (5)
    expect(mockGetWeekScores).toHaveBeenCalledWith('league-1', 5)
  })

  it('navigates to previous week on left arrow click', async () => {
    const wrapper = mount(WeekScoresTab, { props: defaultProps })
    await flushPromises()

    const prevBtn = wrapper.find('[data-testid="prev-week"]')
    await prevBtn.trigger('click')
    await flushPromises()

    expect(mockGetWeekScores).toHaveBeenCalledWith('league-1', 4)
  })

  it('navigates to next week on right arrow click', async () => {
    const wrapper = mount(WeekScoresTab, { props: { ...defaultProps, currentWeek: 5, startWeek: 1 } })
    await flushPromises()

    // Go back first so we can go forward
    const prevBtn = wrapper.find('[data-testid="prev-week"]')
    await prevBtn.trigger('click')
    await flushPromises()

    const nextBtn = wrapper.find('[data-testid="next-week"]')
    await nextBtn.trigger('click')
    await flushPromises()

    expect(mockGetWeekScores).toHaveBeenLastCalledWith('league-1', 5)
  })

  it('handles empty roster slots gracefully', async () => {
    const wrapper = mount(WeekScoresTab, { props: defaultProps })
    await flushPromises()

    // test123's top slot is empty — should show dash
    expect(wrapper.text()).toContain('—')
  })

  it('expands breakdown on click', async () => {
    const wrapper = mount(WeekScoresTab, { props: defaultProps })
    await flushPromises()

    // Click on Faker's row to expand
    const rosterRows = wrapper.findAll('[data-testid="roster-row"]')
    const fakerRow = rosterRows.find(r => r.text().includes('Faker'))
    expect(fakerRow).toBeTruthy()
    await fakerRow!.trigger('click')
    await flushPromises()

    // Should now show breakdown values
    expect(wrapper.text()).toContain('kills')
    expect(wrapper.text()).toContain('10.0')  // value
    expect(wrapper.text()).toContain('24.0 pts')  // points
  })

  it('shows loading spinner while fetching', () => {
    mockGetWeekScores.mockReturnValue(new Promise(() => {}))
    const wrapper = mount(WeekScoresTab, { props: defaultProps })

    expect(wrapper.find('[data-testid="loading-spinner"]').exists()).toBe(true)
  })

  it('shows error state on fetch failure', async () => {
    mockGetWeekScores.mockRejectedValue(new Error('Network error'))
    const wrapper = mount(WeekScoresTab, { props: defaultProps })
    await flushPromises()

    expect(wrapper.text()).toContain('Unable to load scores')
  })
})
