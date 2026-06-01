import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AvailablePlayersTable from '../../src/components/draft/AvailablePlayersTable.vue'
import type { ProfessionalPlayer, ProfessionalTeam } from '../../src/types/riot'

const players: ProfessionalPlayer[] = [
  { id: 'p1', summoner_name: 'Faker', role: 'mid', team_id: 't1', team_name: 'T1', team_code: 'T1', image: '', first_name: '', last_name: '', league_name: 'LCK' },
  { id: 'p2', summoner_name: 'Keria', role: 'support', team_id: 't1', team_name: 'T1', team_code: 'T1', image: '', first_name: '', last_name: '', league_name: 'LCK' },
  { id: 'p3', summoner_name: 'Zeus', role: 'top', team_id: 't1', team_name: 'T1', team_code: 'T1', image: '', first_name: '', last_name: '', league_name: 'LCK' },
]

const teams: ProfessionalTeam[] = [
  { id: 't1', slug: 't1', name: 'T1', code: 'T1', image: '', alternative_image: null, background_image: null, status: 'active', home_league_name: 'LCK', home_league_region: null },
]

const defaultProps = { players, teams, pickDisabled: true }

describe('AvailablePlayersTable', () => {
  it('renders all players when no filter is active', () => {
    const wrapper = mount(AvailablePlayersTable, { props: defaultProps })
    expect(wrapper.text()).toContain('Faker')
    expect(wrapper.text()).toContain('Keria')
    expect(wrapper.text()).toContain('Zeus')
  })

  it('filters players by role when a role tab is clicked', async () => {
    const wrapper = mount(AvailablePlayersTable, { props: defaultProps })
    await wrapper.findAll('button').find(b => b.text() === 'Top')!.trigger('click')
    expect(wrapper.text()).toContain('Zeus')
    expect(wrapper.text()).not.toContain('Faker')
    expect(wrapper.text()).not.toContain('Keria')
  })

  it('filters by search text', async () => {
    const wrapper = mount(AvailablePlayersTable, { props: defaultProps })
    await wrapper.find('input').setValue('faker')
    expect(wrapper.text()).toContain('Faker')
    expect(wrapper.text()).not.toContain('Keria')
  })

  it('shows teams when Team tab is selected', async () => {
    const wrapper = mount(AvailablePlayersTable, { props: defaultProps })
    await wrapper.findAll('button').find(b => b.text() === 'Team')!.trigger('click')
    expect(wrapper.text()).toContain('T1')
    expect(wrapper.text()).not.toContain('Faker')
  })

  it('pick buttons are disabled', () => {
    const wrapper = mount(AvailablePlayersTable, { props: defaultProps })
    const pickButtons = wrapper.findAll('button').filter(b => b.text() === 'Pick')
    expect(pickButtons.length).toBeGreaterThan(0)
    pickButtons.forEach(b => expect((b.element as HTMLButtonElement).disabled).toBe(true))
  })
})
