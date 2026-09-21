import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

// --- router mocks ---
const { mockPush, mockRouteParams } = vi.hoisted(() => ({
  mockPush: vi.fn(),
  mockRouteParams: { value: { id: 'league-1' } as Record<string, string> },
}))

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: mockRouteParams.value }),
  useRouter: () => ({ push: mockPush }),
  RouterLink: { name: 'RouterLink', template: '<a><slot /></a>' },
}))

// --- auth store ---
vi.mock('../../src/stores/auth', () => ({
  useAuthStore: () => ({ userId: 'me' }),
}))

// --- fantasy API ---
const api = vi.hoisted(() => ({
  getLeagueById: vi.fn(),
  getLeagueMembers: vi.fn(),
  getLeagueSettings: vi.fn(),
  getLeagueScoringSettings: vi.fn(),
  getDraftOrder: vi.fn(),
  getLeaderboard: vi.fn(),
  startDraft: vi.fn(),
  leaveLeague: vi.fn(),
}))

vi.mock('../../src/api/fantasyApi', () => api)

import LeagueDetailView from '../../src/views/LeagueDetailView.vue'

const childStubs = {
  LeaderboardTab: { name: 'LeaderboardTab', template: '<div data-stub="standings" />' },
  WeekScoresTab: { name: 'WeekScoresTab', template: '<div data-stub="scores" />' },
  MyRosterTab: { name: 'MyRosterTab', template: '<div data-stub="roster" />' },
  MembersTab: { name: 'MembersTab', template: '<div data-stub="members" />' },
  SettingsTab: { name: 'SettingsTab', template: '<div data-stub="settings" />', methods: { startEditing() {} } },
  ScoringTab: { name: 'ScoringTab', template: '<div data-stub="scoring" />', methods: { startEditing() {} } },
  DraftOrderTab: { name: 'DraftOrderTab', template: '<div data-stub="draft-order" />' },
  InviteMemberModal: { name: 'InviteMemberModal', template: '<div data-stub="invite-modal" />' },
  RouterLink: { name: 'RouterLink', template: '<a><slot /></a>' },
}

function makeLeague(overrides: Record<string, unknown> = {}) {
  return {
    id: 'league-1',
    name: 'My League',
    owner_id: 'owner-1',
    status: 'pre-draft',
    number_of_teams: 2,
    current_week: null,
    current_draft_position: null,
    start_week: null,
    available_leagues: [],
    tournament_id: 't1',
    ...overrides,
  }
}

function mountView() {
  return mount(LeagueDetailView, { global: { stubs: childStubs } })
}

function tabLabels(wrapper: ReturnType<typeof mountView>): string[] {
  return wrapper.findAll('[data-testid="league-tab"]').map((b) => b.text())
}

beforeEach(() => {
  vi.clearAllMocks()
  api.getLeagueMembers.mockResolvedValue([
    { user_id: 'owner-1', username: 'Alice', status: 'accepted' },
    { user_id: 'me', username: 'Me', status: 'accepted' },
  ])
  api.getLeagueSettings.mockResolvedValue({ name: 'My League', number_of_teams: 2, available_leagues: [], tournament_id: 't1' })
  api.getLeagueScoringSettings.mockResolvedValue({ fantasy_league_id: 'league-1' })
  api.getDraftOrder.mockResolvedValue([])
  api.getLeaderboard.mockResolvedValue({
    fantasy_league_id: 'league-1',
    current_week: 8,
    start_week: 1,
    members: [
      { user_id: 'owner-1', username: 'Alice', total_points: 1247.5, position: 1 },
      { user_id: 'me', username: 'Me', total_points: 1198.3, position: 2 },
    ],
  })
})

describe('LeagueDetailView — state-gated tabs', () => {
  it('hides Standings and Scores tabs in pre-draft', async () => {
    api.getLeagueById.mockResolvedValue(makeLeague({ status: 'pre-draft' }))
    const wrapper = mountView()
    await flushPromises()
    const labels = tabLabels(wrapper)
    expect(labels).not.toContain('Standings')
    expect(labels).not.toContain('Scores')
    expect(labels).not.toContain('My Roster')
    expect(labels).toContain('Members')
    expect(labels).toContain('Draft Order')
  })

  it('shows Standings and Scores tabs when active and defaults to Standings', async () => {
    api.getLeagueById.mockResolvedValue(makeLeague({ status: 'active', current_week: 8, start_week: 1 }))
    const wrapper = mountView()
    await flushPromises()
    const labels = tabLabels(wrapper)
    expect(labels).toContain('Standings')
    expect(labels).toContain('Scores')
    expect(labels).toContain('My Roster')
    // default active tab renders standings child
    expect(wrapper.find('[data-stub="standings"]').exists()).toBe(true)
  })

  it('shows hero stat tiles only when active/completed', async () => {
    api.getLeagueById.mockResolvedValue(makeLeague({ status: 'pre-draft' }))
    const preWrapper = mountView()
    await flushPromises()
    expect(preWrapper.find('[data-testid="hero-stats"]').exists()).toBe(false)

    vi.clearAllMocks()
    beforeEachReset()
    api.getLeagueById.mockResolvedValue(makeLeague({ status: 'active', current_week: 8, start_week: 1 }))
    const activeWrapper = mountView()
    await flushPromises()
    expect(activeWrapper.find('[data-testid="hero-stats"]').exists()).toBe(true)
    // rank #2 for current user "me"
    expect(activeWrapper.find('[data-testid="hero-stats"]').text()).toContain('#2')
  })

  it('draft status shows Join Draft and navigates on click', async () => {
    api.getLeagueById.mockResolvedValue(makeLeague({ status: 'draft' }))
    const wrapper = mountView()
    await flushPromises()
    const btn = wrapper.findAll('button').find((b) => b.text().includes('Join Draft'))!
    expect(btn).toBeTruthy()
    await btn.trigger('click')
    expect(mockPush).toHaveBeenCalledWith({ name: 'league-draft', params: { id: 'league-1' } })
  })

  it('owner in pre-draft can start draft (when full) and navigates to draft', async () => {
    api.getLeagueById.mockResolvedValue(makeLeague({ status: 'pre-draft', owner_id: 'me', number_of_teams: 2 }))
    api.startDraft.mockResolvedValue(undefined)
    const wrapper = mountView()
    await flushPromises()
    const btn = wrapper.findAll('button').find((b) => b.text().includes('Start Draft'))!
    expect((btn.element as HTMLButtonElement).disabled).toBe(false)
    await btn.trigger('click')
    await flushPromises()
    expect(api.startDraft).toHaveBeenCalledWith('league-1')
    expect(mockPush).toHaveBeenCalledWith({ name: 'league-draft', params: { id: 'league-1' } })
  })

  it('non-owner in pre-draft can leave and is routed to leagues list', async () => {
    api.getLeagueById.mockResolvedValue(makeLeague({ status: 'pre-draft', owner_id: 'owner-1' }))
    api.leaveLeague.mockResolvedValue(undefined)
    const wrapper = mountView()
    await flushPromises()
    const btn = wrapper.findAll('button').find((b) => b.text().includes('Leave'))!
    await btn.trigger('click')
    await flushPromises()
    expect(api.leaveLeague).toHaveBeenCalledWith('league-1')
    expect(mockPush).toHaveBeenCalledWith({ name: 'leagues' })
  })

  it('shows parent Edit button on Scoring tab for owner in pre-draft', async () => {
    api.getLeagueById.mockResolvedValue(makeLeague({ status: 'pre-draft', owner_id: 'me' }))
    const wrapper = mountView()
    await flushPromises()
    const scoringTab = wrapper.findAll('[data-testid="league-tab"]').find((b) => b.text() === 'Scoring')!
    await scoringTab.trigger('click')
    const editBtn = wrapper.findAll('button').find((b) => b.text() === 'Edit')
    expect(editBtn).toBeTruthy()
  })

  it('opens the invite modal when the hero Invite button is clicked (owner, pre-draft)', async () => {
    api.getLeagueById.mockResolvedValue(makeLeague({ status: 'pre-draft', owner_id: 'me' }))
    const wrapper = mountView()
    await flushPromises()

    // modal not open initially
    expect(wrapper.find('[data-stub="invite-modal"]').exists()).toBe(false)

    const inviteBtn = wrapper.findAll('button').find((b) => b.text().includes('Invite friends'))!
    expect(inviteBtn).toBeTruthy()
    await inviteBtn.trigger('click')

    expect(wrapper.find('[data-stub="invite-modal"]').exists()).toBe(true)
  })
})

// helper to re-seed the API mocks after clearAllMocks within a single test
function beforeEachReset() {
  api.getLeagueMembers.mockResolvedValue([
    { user_id: 'owner-1', username: 'Alice', status: 'accepted' },
    { user_id: 'me', username: 'Me', status: 'accepted' },
  ])
  api.getLeagueSettings.mockResolvedValue({ name: 'My League', number_of_teams: 2, available_leagues: [], tournament_id: 't1' })
  api.getLeagueScoringSettings.mockResolvedValue({ fantasy_league_id: 'league-1' })
  api.getDraftOrder.mockResolvedValue([])
  api.getLeaderboard.mockResolvedValue({
    fantasy_league_id: 'league-1',
    current_week: 8,
    start_week: 1,
    members: [
      { user_id: 'owner-1', username: 'Alice', total_points: 1247.5, position: 1 },
      { user_id: 'me', username: 'Me', total_points: 1198.3, position: 2 },
    ],
  })
}
