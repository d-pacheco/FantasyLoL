import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import MembersTab from '../../src/components/leagues/MembersTab.vue'

const members = [
  { user_id: 'u1', username: 'Alice', status: 'accepted' as const },
  { user_id: 'u2', username: 'Bob', status: 'pending' as const },
]

const defaultProps = {
  members,
  ownerId: 'u1',
  loading: false,
  error: '',
}

describe('MembersTab', () => {
  it('shows the member list', () => {
    const wrapper = mount(MembersTab, { props: defaultProps })
    expect(wrapper.text()).toContain('Alice')
    expect(wrapper.text()).toContain('Bob')
  })

  it('does not render an inline invite section (invites live in a modal now)', () => {
    const wrapper = mount(MembersTab, { props: defaultProps })
    expect(wrapper.text()).not.toContain('Invite Player')
    expect(wrapper.find('input[placeholder="Enter username..."]').exists()).toBe(false)
  })

  it('renders one card per member with a status badge', () => {
    const wrapper = mount(MembersTab, { props: defaultProps })
    const cards = wrapper.findAll('[data-testid="member-card"]')
    expect(cards.length).toBe(2)
    const alice = cards.find(c => c.text().includes('Alice'))!
    expect(alice.text().toLowerCase()).toContain('accepted')
    const bob = cards.find(c => c.text().includes('Bob'))!
    expect(bob.text().toLowerCase()).toContain('pending')
  })

  it('marks the owner member with an owner badge', () => {
    const wrapper = mount(MembersTab, { props: defaultProps })
    const badge = wrapper.find('[data-testid="owner-badge"]')
    expect(badge.exists()).toBe(true)
    const cards = wrapper.findAll('[data-testid="member-card"]')
    const alice = cards.find(c => c.text().includes('Alice'))!
    expect(alice.find('[data-testid="owner-badge"]').exists()).toBe(true)
  })
})
