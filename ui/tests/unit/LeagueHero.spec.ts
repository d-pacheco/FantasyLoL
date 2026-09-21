import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LeagueHero from '../../src/components/leagues/LeagueHero.vue'
import type { FantasyLeague } from '../../src/types/fantasy'
import type { LeagueMember } from '../../src/api/fantasyApi'

const baseLeague: FantasyLeague = {
  id: 'league-1',
  name: 'Worlds Fantasy 2024',
  owner_id: 'owner-1',
  status: 'pre-draft',
  number_of_teams: 4,
  current_week: null,
  current_draft_position: null,
  start_week: null,
  available_leagues: [],
  tournament_id: 't1',
}

const members: LeagueMember[] = [
  { user_id: 'owner-1', username: 'Alice', status: 'accepted' },
  { user_id: 'u2', username: 'Bob', status: 'accepted' },
  { user_id: 'u3', username: 'Cara', status: 'pending' },
]

const fullMembers: LeagueMember[] = [
  { user_id: 'owner-1', username: 'Alice', status: 'accepted' },
  { user_id: 'u2', username: 'Bob', status: 'accepted' },
  { user_id: 'u3', username: 'Cara', status: 'accepted' },
  { user_id: 'u4', username: 'Dee', status: 'accepted' },
]

function factory(overrides: Record<string, unknown> = {}) {
  return mount(LeagueHero, {
    props: {
      league: baseLeague,
      members,
      isOwner: false,
      currentUserId: 'u2',
      starting: false,
      leaving: false,
      startError: '',
      stats: null,
      ...overrides,
    },
  })
}

describe('LeagueHero', () => {
  it('renders league name and status', () => {
    const wrapper = factory()
    expect(wrapper.text()).toContain('Worlds Fantasy 2024')
    expect(wrapper.text()).toContain('pre-draft')
  })

  it('shows accepted member count against capacity', () => {
    const wrapper = factory()
    const count = wrapper.find('[data-testid="member-count"]')
    expect(count.exists()).toBe(true)
    // 2 accepted of 4 capacity
    expect(count.text()).toContain('2')
    expect(count.text()).toContain('4')
  })

  it('hides stat tiles when no stats provided (pre-draft/draft)', () => {
    const wrapper = factory({ stats: null })
    expect(wrapper.find('[data-testid="hero-stats"]').exists()).toBe(false)
  })

  it('shows stat tiles when stats provided (active/completed)', () => {
    const wrapper = factory({
      league: { ...baseLeague, status: 'active' },
      stats: { rank: 2, points: 1198.3, pointsBehind: 49.2, week: 8 },
    })
    const stats = wrapper.find('[data-testid="hero-stats"]')
    expect(stats.exists()).toBe(true)
    expect(stats.text()).toContain('#2')
    expect(stats.text()).toContain('8') // week
  })

  it('owner in pre-draft sees a disabled Start Draft with "need N more" when not full', () => {
    const wrapper = factory({ isOwner: true })
    const btn = wrapper.findAll('button').find((b) => b.text().includes('Start Draft'))!
    expect(btn).toBeTruthy()
    expect((btn.element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.text()).toContain('Need 2 more')
  })

  it('owner in pre-draft can start draft when full', async () => {
    const wrapper = factory({ isOwner: true, members: fullMembers })
    const btn = wrapper.findAll('button').find((b) => b.text().includes('Start Draft'))!
    expect((btn.element as HTMLButtonElement).disabled).toBe(false)
    await btn.trigger('click')
    expect(wrapper.emitted('start-draft')).toBeTruthy()
  })

  it('non-owner in pre-draft sees Leave League and emits leave on click', async () => {
    const wrapper = factory({ isOwner: false })
    const btn = wrapper.findAll('button').find((b) => b.text().includes('Leave'))!
    expect(btn).toBeTruthy()
    await btn.trigger('click')
    expect(wrapper.emitted('leave')).toBeTruthy()
  })

  it('draft status shows Join Draft and emits join-draft on click', async () => {
    const wrapper = factory({ league: { ...baseLeague, status: 'draft' } })
    const btn = wrapper.findAll('button').find((b) => b.text().includes('Join Draft'))!
    expect(btn).toBeTruthy()
    await btn.trigger('click')
    expect(wrapper.emitted('join-draft')).toBeTruthy()
  })

  it('shows start draft error when provided', () => {
    const wrapper = factory({ isOwner: true, startError: 'Failed to start draft.' })
    expect(wrapper.text()).toContain('Failed to start draft.')
  })

  it('does not show Start/Leave/Join actions when active', () => {
    const wrapper = factory({
      league: { ...baseLeague, status: 'active' },
      stats: { rank: 1, points: 100, pointsBehind: 0, week: 3 },
    })
    const labels = wrapper.findAll('button').map((b) => b.text())
    expect(labels.some((t) => t.includes('Start Draft'))).toBe(false)
    expect(labels.some((t) => t.includes('Join Draft'))).toBe(false)
    expect(labels.some((t) => t.includes('Leave'))).toBe(false)
  })
})
