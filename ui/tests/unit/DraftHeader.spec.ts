import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DraftHeader from '../../src/components/draft/DraftHeader.vue'

const defaultProps = {
  leagueName: 'Test League',
  currentRound: 2,
  totalRounds: 6,
  currentPickNumber: 7,
  totalPicks: 24,
  currentTurnUsername: 'User3',
  isYourTurn: false,
}

describe('DraftHeader', () => {
  it('renders league name, round, and pick number', () => {
    const wrapper = mount(DraftHeader, { props: defaultProps })
    expect(wrapper.text()).toContain('Test League')
    expect(wrapper.text()).toContain('Round 2 of 6')
    expect(wrapper.text()).toContain('Pick 7 of 24')
  })

  it('shows "Your turn!" when isYourTurn is true', () => {
    const wrapper = mount(DraftHeader, { props: { ...defaultProps, isYourTurn: true } })
    expect(wrapper.text()).toContain('Your turn!')
  })

  it("shows picker's username when it is not your turn", () => {
    const wrapper = mount(DraftHeader, { props: defaultProps })
    expect(wrapper.text()).toContain("User3's turn")
  })
})
