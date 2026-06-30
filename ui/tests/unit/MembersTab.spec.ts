import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { mockInviteToLeague } = vi.hoisted(() => ({
  mockInviteToLeague: vi.fn(),
}))

vi.mock('../../src/api/fantasyApi', () => ({
  inviteToLeague: mockInviteToLeague,
}))

import MembersTab from '../../src/components/leagues/MembersTab.vue'

const members = [
  { user_id: 'u1', username: 'Alice', status: 'accepted' as const },
  { user_id: 'u2', username: 'Bob', status: 'pending' as const },
]

const defaultProps = {
  leagueId: 'league-1',
  members,
  editable: false,
  ownerId: 'u1',
  loading: false,
  error: '',
}

describe('MembersTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows member list but hides invite section when editable is false', () => {
    const wrapper = mount(MembersTab, { props: defaultProps })
    expect(wrapper.text()).toContain('Alice')
    expect(wrapper.text()).toContain('Bob')
    expect(wrapper.text()).not.toContain('Invite Player')
    expect(wrapper.find('input[placeholder="Enter username..."]').exists()).toBe(false)
  })

  it('shows invite section when editable is true', () => {
    const wrapper = mount(MembersTab, { props: { ...defaultProps, editable: true } })
    expect(wrapper.text()).toContain('Invite Player')
    expect(wrapper.find('input[placeholder="Enter username..."]').exists()).toBe(true)
  })

  it('sends invite and emits invited event on success', async () => {
    mockInviteToLeague.mockResolvedValue(undefined)
    const wrapper = mount(MembersTab, { props: { ...defaultProps, editable: true } })

    const input = wrapper.find('input[placeholder="Enter username..."]')
    await input.setValue('Charlie')

    const sendBtn = wrapper.findAll('button').find(b => b.text().includes('Send'))!
    await sendBtn.trigger('click')
    await flushPromises()

    expect(mockInviteToLeague).toHaveBeenCalledWith('league-1', 'Charlie')
    expect(wrapper.emitted('invited')).toBeTruthy()
    expect(wrapper.emitted('invited')![0]).toEqual(['Charlie'])
  })
})
