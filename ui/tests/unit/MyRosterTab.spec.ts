import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { mockGetWeekScores } = vi.hoisted(() => ({
  mockGetWeekScores: vi.fn(),
}))
const { mockGetPlayerById, mockGetTeamById } = vi.hoisted(() => ({
  mockGetPlayerById: vi.fn(),
  mockGetTeamById: vi.fn(),
}))

vi.mock('../../src/api/fantasyApi', () => ({
  getWeekScores: mockGetWeekScores,
}))

vi.mock('../../src/api/riotApi', () => ({
  getPlayerById: mockGetPlayerById,
  getTeamById: mockGetTeamById,
}))

vi.mock('../../src/stores/auth', () => ({
  useAuthStore: () => ({ userId: 'u1' }),
}))

import MyRosterTab from '../../src/components/leagues/MyRosterTab.vue'

const weekScores = {
  fantasy_league_id: 'league-1',
  week: 5,
  members: [
    {
      user_id: 'u1',
      username: 'Me',
      total_points: 142.5,
      roster: {
        top: { player_id: 'p1', summoner_name: 'Zeus', points: 28.3, breakdown: {} },
        jungle: { player_id: 'p2', summoner_name: 'Oner', points: 31.1, breakdown: {} },
        mid: { player_id: 'p3', summoner_name: 'Faker', points: 42.7, breakdown: {} },
        adc: { player_id: 'p4', summoner_name: 'Gumayusi', points: 22.4, breakdown: {} },
        support: { player_id: 'p5', summoner_name: 'Keria', points: 12.0, breakdown: {} },
        team: { team_id: 't1', team_name: 'T1', points: 6.0, breakdown: {} },
      },
    },
    { user_id: 'u2', username: 'Other', total_points: 100, roster: {} },
  ],
}

function playerFixture(id: string) {
  return {
    id,
    summoner_name: '',
    first_name: '',
    last_name: '',
    image: `https://img/${id}.png`,
    role: 'mid',
    team_id: 't1',
    team_name: 'T1',
    team_code: 'T1',
    league_name: 'LCK',
  }
}

const teamFixture = {
  id: 't1',
  slug: 't1',
  name: 'T1',
  code: 'T1',
  image: 'https://img/t1.png',
  alternative_image: null,
  background_image: null,
  status: 'active',
  home_league_name: null,
  home_league_region: null,
}

const defaultProps = { leagueId: 'league-1', currentWeek: 5 }

describe('MyRosterTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetWeekScores.mockResolvedValue(weekScores)
    mockGetPlayerById.mockImplementation((id: string) => Promise.resolve(playerFixture(id)))
    mockGetTeamById.mockResolvedValue(teamFixture)
  })

  it('fetches the current week for the league', async () => {
    mount(MyRosterTab, { props: defaultProps })
    await flushPromises()
    expect(mockGetWeekScores).toHaveBeenCalledWith('league-1', 5)
  })

  it("shows the current user's players with names and points", async () => {
    const wrapper = mount(MyRosterTab, { props: defaultProps })
    await flushPromises()
    expect(wrapper.text()).toContain('Faker')
    expect(wrapper.text()).toContain('42.7')
    expect(wrapper.text()).toContain('Zeus')
    expect(wrapper.text()).toContain('Keria')
    expect(wrapper.text()).toContain('T1')
  })

  it('shows the weekly total points', async () => {
    const wrapper = mount(MyRosterTab, { props: defaultProps })
    await flushPromises()
    expect(wrapper.text()).toContain('142.5')
  })

  it('renders a slot for each position including team', async () => {
    const wrapper = mount(MyRosterTab, { props: defaultProps })
    await flushPromises()
    expect(wrapper.findAll('[data-testid="roster-slot"]').length).toBe(6)
  })

  it('renders player icons for each drafted player', async () => {
    const wrapper = mount(MyRosterTab, { props: defaultProps })
    await flushPromises()
    expect(mockGetPlayerById).toHaveBeenCalledWith('p3')
    const fakerImg = wrapper.find('img[alt="Faker"]')
    expect(fakerImg.exists()).toBe(true)
    expect(fakerImg.attributes('src')).toBe('https://img/p3.png')
  })

  it('renders the team icon for the team slot', async () => {
    const wrapper = mount(MyRosterTab, { props: defaultProps })
    await flushPromises()
    expect(mockGetTeamById).toHaveBeenCalledWith('t1')
    const teamImg = wrapper.find('img[alt="T1"]')
    expect(teamImg.exists()).toBe(true)
    expect(teamImg.attributes('src')).toBe('https://img/t1.png')
  })

  it('falls back to initials when a player icon fails to load', async () => {
    mockGetPlayerById.mockImplementation((id: string) => {
      if (id === 'p1') return Promise.reject(new Error('not found'))
      return Promise.resolve(playerFixture(id))
    })
    const wrapper = mount(MyRosterTab, { props: defaultProps })
    await flushPromises()
    // Zeus has no image -> no img with that alt, but name still shows
    expect(wrapper.find('img[alt="Zeus"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('Zeus')
    // other players still have icons
    expect(wrapper.find('img[alt="Faker"]').exists()).toBe(true)
  })

  it('does not show another members players', async () => {
    const wrapper = mount(MyRosterTab, { props: defaultProps })
    await flushPromises()
    expect(wrapper.text()).not.toContain('Other')
  })

  it('shows an empty state when the user has no team this week', async () => {
    mockGetWeekScores.mockResolvedValue({
      ...weekScores,
      members: [{ user_id: 'u2', username: 'Other', total_points: 100, roster: {} }],
    })
    const wrapper = mount(MyRosterTab, { props: defaultProps })
    await flushPromises()
    expect(wrapper.findAll('[data-testid="roster-slot"]').length).toBe(0)
    expect(wrapper.text().toLowerCase()).toContain('roster')
  })

  it('shows a loading spinner while fetching', () => {
    mockGetWeekScores.mockReturnValue(new Promise(() => {}))
    const wrapper = mount(MyRosterTab, { props: defaultProps })
    expect(wrapper.find('[data-testid="loading-spinner"]').exists()).toBe(true)
  })

  it('shows an error state on fetch failure', async () => {
    mockGetWeekScores.mockRejectedValue(new Error('Network error'))
    const wrapper = mount(MyRosterTab, { props: defaultProps })
    await flushPromises()
    expect(wrapper.text()).toContain('Unable to load roster')
  })
})
