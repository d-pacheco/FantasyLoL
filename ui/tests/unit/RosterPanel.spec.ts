import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RosterPanel from '../../src/components/draft/RosterPanel.vue'
import type { UserSlots } from '../../src/types/fantasy'
import type { ProfessionalPlayer } from '../../src/types/riot'

const emptySlots: UserSlots = {
  top_player_id: null,
  jungle_player_id: null,
  mid_player_id: null,
  adc_player_id: null,
  support_player_id: null,
  team_id: null,
}

const players: ProfessionalPlayer[] = [
  { id: 'p1', summoner_name: 'Faker', role: 'mid', team_id: 't1', team_name: 'T1', team_code: 'T1', image: '', first_name: '', last_name: '', league_name: 'LCK' },
]

describe('RosterPanel', () => {
  it('shows all 6 slot labels', () => {
    const wrapper = mount(RosterPanel, { props: { slots: emptySlots, players } })
    expect(wrapper.text()).toContain('TOP')
    expect(wrapper.text()).toContain('JGL')
    expect(wrapper.text()).toContain('MID')
    expect(wrapper.text()).toContain('ADC')
    expect(wrapper.text()).toContain('SUP')
    expect(wrapper.text()).toContain('TEAM')
  })

  it('shows player name for a filled slot', () => {
    const slots: UserSlots = { ...emptySlots, mid_player_id: 'p1' }
    const wrapper = mount(RosterPanel, { props: { slots, players } })
    expect(wrapper.text()).toContain('Faker')
  })

  it('shows placeholder for an empty slot', () => {
    const wrapper = mount(RosterPanel, { props: { slots: emptySlots, players } })
    expect(wrapper.text()).toContain('empty')
  })
})
