import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PickHistoryTicker from '../../src/components/draft/PickHistoryTicker.vue'
import type { DraftPick } from '../../src/types/fantasy'
import type { ProfessionalPlayer, ProfessionalTeam } from '../../src/types/riot'
import type { DraftOrderEntry } from '../../src/api/fantasyApi'

const players: ProfessionalPlayer[] = [
  { id: 'p1', summoner_name: 'Faker', role: 'mid', team_id: 't1', team_name: 'T1', team_code: 'T1', image: '', first_name: '', last_name: '', league_name: 'LCK' },
  { id: 'p2', summoner_name: 'Keria', role: 'support', team_id: 't1', team_name: 'T1', team_code: 'T1', image: '', first_name: '', last_name: '', league_name: 'LCK' },
]
const teams: ProfessionalTeam[] = []
const draftOrder: DraftOrderEntry[] = [
  { user_id: 'u1', username: 'User1', position: 1 },
  { user_id: 'u2', username: 'User2', position: 2 },
]
const picks: DraftPick[] = [
  { fantasy_league_id: 'l1', pick_number: 1, round_number: 1, user_id: 'u1', player_id: 'p1', team_id: null },
  { fantasy_league_id: 'l1', pick_number: 2, round_number: 1, user_id: 'u2', player_id: 'p2', team_id: null },
]

describe('PickHistoryTicker', () => {
  it('renders pick number and player name for each pick', () => {
    const wrapper = mount(PickHistoryTicker, { props: { picks, players, teams, draftOrder } })
    expect(wrapper.text()).toContain('#1')
    expect(wrapper.text()).toContain('Faker')
    expect(wrapper.text()).toContain('#2')
    expect(wrapper.text()).toContain('Keria')
  })

  it('shows most recent pick first', () => {
    const wrapper = mount(PickHistoryTicker, { props: { picks, players, teams, draftOrder } })
    const text = wrapper.text()
    expect(text.indexOf('#2')).toBeLessThan(text.indexOf('#1'))
  })
})
