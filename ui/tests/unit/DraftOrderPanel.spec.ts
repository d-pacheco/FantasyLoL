import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DraftOrderPanel from '../../src/components/draft/DraftOrderPanel.vue'
import type { DraftOrderEntry } from '../../src/api/fantasyApi'
import type { UserSlots } from '../../src/types/fantasy'

const draftOrder: DraftOrderEntry[] = [
  { user_id: 'u1', username: 'User1', position: 1 },
  { user_id: 'u2', username: 'User2', position: 2 },
  { user_id: 'u3', username: 'User3', position: 3 },
]

const userSlots: Record<string, UserSlots> = {
  u1: { top_player_id: 'p1', jungle_player_id: 'p2', mid_player_id: null, adc_player_id: null, support_player_id: null, team_id: null },
  u2: { top_player_id: 'p3', jungle_player_id: null, mid_player_id: null, adc_player_id: null, support_player_id: null, team_id: null },
}

describe('DraftOrderPanel', () => {
  it('renders all members with their username', () => {
    const wrapper = mount(DraftOrderPanel, { props: { draftOrder, userSlots, currentTurnUserId: 'u3' } })
    expect(wrapper.text()).toContain('User1')
    expect(wrapper.text()).toContain('User2')
    expect(wrapper.text()).toContain('User3')
  })

  it('highlights the current picker', () => {
    const wrapper = mount(DraftOrderPanel, { props: { draftOrder, userSlots, currentTurnUserId: 'u3' } })
    const rows = wrapper.findAll('[class*="bg-primary"]')
    expect(rows.some(r => r.text().includes('User3'))).toBe(true)
  })

  it('shows pick count for each member', () => {
    const wrapper = mount(DraftOrderPanel, { props: { draftOrder, userSlots, currentTurnUserId: 'u3' } })
    expect(wrapper.text()).toContain('2 picks') // u1 has 2
    expect(wrapper.text()).toContain('1 picks') // u2 has 1
  })
})
