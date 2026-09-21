import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { mockInviteToLeague } = vi.hoisted(() => ({
  mockInviteToLeague: vi.fn(),
}))

vi.mock('../../src/api/fantasyApi', () => ({
  inviteToLeague: mockInviteToLeague,
}))

import InviteMemberModal from '../../src/components/leagues/InviteMemberModal.vue'

const props = { leagueId: 'league-1' }
const INPUT = 'input[placeholder="Enter username..."]'

function sendButton(wrapper: ReturnType<typeof mount>) {
  return wrapper.findAll('button').find((b) => b.text().includes('Send Invite'))!
}

describe('InviteMemberModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders a username input with Send disabled until text is entered', async () => {
    const wrapper = mount(InviteMemberModal, { props })
    const input = wrapper.find(INPUT)
    expect(input.exists()).toBe(true)
    expect((sendButton(wrapper).element as HTMLButtonElement).disabled).toBe(true)

    await input.setValue('Charlie')
    expect((sendButton(wrapper).element as HTMLButtonElement).disabled).toBe(false)
  })

  it('sends the invite, emits invited, clears input, and stays open with confirmation', async () => {
    mockInviteToLeague.mockResolvedValue(undefined)
    const wrapper = mount(InviteMemberModal, { props })

    await wrapper.find(INPUT).setValue('Charlie')
    await sendButton(wrapper).trigger('click')
    await flushPromises()

    expect(mockInviteToLeague).toHaveBeenCalledWith('league-1', 'Charlie')
    expect(wrapper.emitted('invited')).toBeTruthy()
    expect(wrapper.emitted('invited')![0]).toEqual(['Charlie'])
    // still open (not closed), input cleared, confirmation shown
    expect(wrapper.emitted('close')).toBeFalsy()
    expect((wrapper.find(INPUT).element as HTMLInputElement).value).toBe('')
    expect(wrapper.text()).toContain('Invited Charlie')
  })

  it('shows "User not found." on 404', async () => {
    mockInviteToLeague.mockRejectedValue({ response: { status: 404 } })
    const wrapper = mount(InviteMemberModal, { props })
    await wrapper.find(INPUT).setValue('Ghost')
    await sendButton(wrapper).trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('User not found.')
    expect(wrapper.emitted('invited')).toBeFalsy()
  })

  it('shows a conflict message on 409', async () => {
    mockInviteToLeague.mockRejectedValue({ response: { status: 409 } })
    const wrapper = mount(InviteMemberModal, { props })
    await wrapper.find(INPUT).setValue('Dupe')
    await sendButton(wrapper).trigger('click')
    await flushPromises()
    expect(wrapper.text().toLowerCase()).toContain('already invited')
  })

  it('emits close when Cancel is clicked', async () => {
    const wrapper = mount(InviteMemberModal, { props })
    const cancel = wrapper.findAll('button').find((b) => b.text() === 'Cancel')!
    await cancel.trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('emits close on backdrop click', async () => {
    const wrapper = mount(InviteMemberModal, { props })
    await wrapper.trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
