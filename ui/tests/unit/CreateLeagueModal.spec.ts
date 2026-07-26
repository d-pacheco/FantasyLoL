import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { mockGetRiotLeagues, mockGetTournaments } = vi.hoisted(() => ({
  mockGetRiotLeagues: vi.fn(),
  mockGetTournaments: vi.fn(),
}))

const { mockCreateLeague } = vi.hoisted(() => ({
  mockCreateLeague: vi.fn(),
}))

vi.mock('../../src/api/riotApi', () => ({
  getRiotLeagues: mockGetRiotLeagues,
  getTournaments: mockGetTournaments,
}))

vi.mock('../../src/api/fantasyApi', () => ({
  createLeague: mockCreateLeague,
}))

import CreateLeagueModal from '../../src/components/leagues/CreateLeagueModal.vue'

const lcsLeague = {
  id: 'riot-league-lcs',
  slug: 'lcs',
  name: 'LCS',
  region: 'North America',
  image: 'https://example.com/lcs.png',
  priority: 1,
  fantasy_available: true,
}

const lecLeague = {
  id: 'riot-league-lec',
  slug: 'lec',
  name: 'LEC',
  region: 'Europe',
  image: 'https://example.com/lec.png',
  priority: 2,
  fantasy_available: true,
}

const activeTournament = {
  id: 'tournament-active',
  slug: 'lcs_split_1_2026',
  start_date: '2020-01-01',
  end_date: '2999-01-01',
  league_id: 'riot-league-lcs',
}

const upcomingTournament = {
  id: 'tournament-upcoming',
  slug: 'lcs_split_2_2026',
  start_date: '2999-01-01',
  end_date: '2999-06-01',
  league_id: 'riot-league-lcs',
}

const completedTournament = {
  id: 'tournament-completed',
  slug: 'lcs_split_0_2025',
  start_date: '2020-01-01',
  end_date: '2020-06-01',
  league_id: 'riot-league-lcs',
}

const otherLeagueTournament = {
  id: 'tournament-lec',
  slug: 'lec_split_1_2026',
  start_date: '2020-01-01',
  end_date: '2999-01-01',
  league_id: 'riot-league-lec',
}

describe('CreateLeagueModal - tournament selector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetRiotLeagues.mockResolvedValue({ items: [lcsLeague, lecLeague] })
    mockGetTournaments.mockResolvedValue({
      items: [activeTournament, upcomingTournament, completedTournament, otherLeagueTournament],
    })
  })

  it('does not show the tournament dropdown before a league is selected', async () => {
    const wrapper = mount(CreateLeagueModal)
    await flushPromises()

    expect(wrapper.text()).not.toContain('LCS SPLIT 1 2026')
  })

  it('shows the tournament dropdown filtered to the selected league after selecting a league', async () => {
    const wrapper = mount(CreateLeagueModal)
    await flushPromises()

    const lcsButton = wrapper.findAll('button').find(b => b.text().includes('LCS'))!
    await lcsButton.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('LCS SPLIT 1 2026')
    expect(wrapper.text()).toContain('LCS SPLIT 2 2026')
    expect(wrapper.text()).not.toContain('LCS SPLIT 0 2025')
    expect(wrapper.text()).not.toContain('LEC SPLIT 1 2026')
  })

  it('resets tournament selection and re-filters when the selected league changes', async () => {
    const wrapper = mount(CreateLeagueModal)
    await flushPromises()

    const lcsButton = wrapper.findAll('button').find(b => b.text().includes('LCS'))!
    await lcsButton.trigger('click')
    await flushPromises()

    const tournamentButton = wrapper.findAll('button').find(b => b.text().includes('LCS SPLIT 1 2026'))!
    await tournamentButton.trigger('click')
    await flushPromises()
    expect(tournamentButton.classes().join(' ')).toContain('text-primary')

    // Switch to LEC
    const lecButton = wrapper.findAll('button').find(b => b.text().includes('LEC'))!
    await lecButton.trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('LCS SPLIT 1 2026')
    expect(wrapper.text()).toContain('LEC SPLIT 1 2026')
  })

  it('disables the Create button until both a league and tournament are selected', async () => {
    const wrapper = mount(CreateLeagueModal)
    await flushPromises()

    const nameInput = wrapper.find('input[type="text"]')
    await nameInput.setValue('My League')

    const createBtn = wrapper.findAll('button').find(b => b.text() === 'Create League')!
    expect((createBtn.element as HTMLButtonElement).disabled).toBe(true)

    const lcsButton = wrapper.findAll('button').find(b => b.text().includes('LCS'))!
    await lcsButton.trigger('click')
    await flushPromises()
    expect((createBtn.element as HTMLButtonElement).disabled).toBe(true)

    const tournamentButton = wrapper.findAll('button').find(b => b.text().includes('LCS SPLIT 1 2026'))!
    await tournamentButton.trigger('click')
    await flushPromises()
    expect((createBtn.element as HTMLButtonElement).disabled).toBe(false)
  })

  it('includes tournament_id in the createLeague payload on submit', async () => {
    mockCreateLeague.mockResolvedValue({ id: 'league-1' })
    const wrapper = mount(CreateLeagueModal)
    await flushPromises()

    const nameInput = wrapper.find('input[type="text"]')
    await nameInput.setValue('My League')

    const lcsButton = wrapper.findAll('button').find(b => b.text().includes('LCS'))!
    await lcsButton.trigger('click')
    await flushPromises()

    const tournamentButton = wrapper.findAll('button').find(b => b.text().includes('LCS SPLIT 1 2026'))!
    await tournamentButton.trigger('click')
    await flushPromises()

    const createBtn = wrapper.findAll('button').find(b => b.text() === 'Create League')!
    await createBtn.trigger('click')
    await flushPromises()

    expect(mockCreateLeague).toHaveBeenCalledWith({
      name: 'My League',
      number_of_teams: 6,
      available_leagues: ['riot-league-lcs'],
      tournament_id: 'tournament-active',
    })
  })

  it('shows a message when no active or upcoming tournaments exist for the selected league', async () => {
    mockGetTournaments.mockResolvedValue({ items: [completedTournament] })
    const wrapper = mount(CreateLeagueModal)
    await flushPromises()

    const lcsButton = wrapper.findAll('button').find(b => b.text().includes('LCS'))!
    await lcsButton.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('No active or upcoming tournaments available for this league.')
  })
})
