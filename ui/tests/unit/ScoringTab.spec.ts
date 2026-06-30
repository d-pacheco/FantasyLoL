import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { mockUpdateLeagueScoringSettings } = vi.hoisted(() => ({
  mockUpdateLeagueScoringSettings: vi.fn(),
}))

vi.mock('../../src/api/fantasyApi', () => ({
  updateLeagueScoringSettings: mockUpdateLeagueScoringSettings,
}))

import ScoringTab from '../../src/components/leagues/ScoringTab.vue'

const defaultScoring = {
  fantasy_league_id: 'league-1',
  kills: 3,
  deaths: -1,
  assists: 2,
  cspm: 0.5,
  wards_placed: 0.1,
  wards_destroyed: 0.2,
  kill_participation: 1,
  damage_percentage: 1,
  double_kill: 2,
  triple_kill: 3,
  quadra_kill: 5,
  penta_kill: 10,
  match_win: 5,
  match_sweep: 3,
  dragon: 2,
  elder_dragon: 4,
  baron: 3,
  tower: 1,
  inhibitor: 2,
  soul: 5,
}

const defaultProps = {
  scoring: defaultScoring,
  loading: false,
  error: '',
  editable: false,
  leagueId: 'league-1',
}

describe('ScoringTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays scoring values in read-only mode', () => {
    const wrapper = mount(ScoringTab, { props: defaultProps })
    expect(wrapper.text()).toContain('Kills')
    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).toContain('Deaths')
    expect(wrapper.text()).toContain('-1')
  })

  it('exposes startEditing and shows numeric inputs when called', async () => {
    const wrapper = mount(ScoringTab, {
      props: { ...defaultProps, editable: true },
    })

    ;(wrapper.vm as unknown as { startEditing: () => void }).startEditing()
    await flushPromises()

    const inputs = wrapper.findAll('input[type="number"]')
    expect(inputs.length).toBe(20)

    // Check kills input is pre-populated
    const killsInput = inputs[0]
    expect((killsInput.element as HTMLInputElement).value).toBe('3')

    expect(wrapper.text()).toContain('Save')
    expect(wrapper.text()).toContain('Cancel')
  })

  it('clicking Cancel exits edit mode without saving', async () => {
    const wrapper = mount(ScoringTab, {
      props: { ...defaultProps, editable: true },
    })

    ;(wrapper.vm as unknown as { startEditing: () => void }).startEditing()
    await flushPromises()

    // Modify kills
    const inputs = wrapper.findAll('input[type="number"]')
    await inputs[0].setValue('99')

    // Click Cancel
    const cancelBtn = wrapper.findAll('button').find(b => b.text() === 'Cancel')!
    await cancelBtn.trigger('click')
    await flushPromises()

    // Should be back in read-only mode
    expect(wrapper.findAll('input[type="number"]').length).toBe(0)
    expect(wrapper.text()).toContain('3')
    expect(mockUpdateLeagueScoringSettings).not.toHaveBeenCalled()
  })

  it('successful save calls API and emits updated event', async () => {
    const updatedScoring = { ...defaultScoring, kills: 5 }
    mockUpdateLeagueScoringSettings.mockResolvedValue(updatedScoring)

    const wrapper = mount(ScoringTab, {
      props: { ...defaultProps, editable: true },
    })

    ;(wrapper.vm as unknown as { startEditing: () => void }).startEditing()
    await flushPromises()

    // Change kills to 5
    const inputs = wrapper.findAll('input[type="number"]')
    await inputs[0].setValue('5')

    // Click Save
    const saveBtn = wrapper.findAll('button').find(b => b.text() === 'Save')!
    await saveBtn.trigger('click')
    await flushPromises()

    expect(mockUpdateLeagueScoringSettings).toHaveBeenCalledWith('league-1', expect.objectContaining({
      fantasy_league_id: null,
      kills: 5,
      deaths: -1,
    }))
    expect(wrapper.emitted('updated')).toBeTruthy()
    expect(wrapper.emitted('updated')![0]).toEqual([updatedScoring])

    // Should exit edit mode
    expect(wrapper.findAll('input[type="number"]').length).toBe(0)
  })

  it('displays inline error when save fails', async () => {
    mockUpdateLeagueScoringSettings.mockRejectedValue({
      response: { data: { detail: 'Forbidden' } },
    })

    const wrapper = mount(ScoringTab, {
      props: { ...defaultProps, editable: true },
    })

    ;(wrapper.vm as unknown as { startEditing: () => void }).startEditing()
    await flushPromises()

    // Click Save
    const saveBtn = wrapper.findAll('button').find(b => b.text() === 'Save')!
    await saveBtn.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Forbidden')
    // Should still be in edit mode
    expect(wrapper.findAll('input[type="number"]').length).toBe(20)
  })

  it('rounds integer fields (kills, deaths, kill_participation, damage_percentage) on save', async () => {
    mockUpdateLeagueScoringSettings.mockResolvedValue(defaultScoring)

    const wrapper = mount(ScoringTab, {
      props: { ...defaultProps, editable: true },
    })

    ;(wrapper.vm as unknown as { startEditing: () => void }).startEditing()
    await flushPromises()

    // Set kills to a fractional value
    const inputs = wrapper.findAll('input[type="number"]')
    await inputs[0].setValue('3.7') // kills

    const saveBtn = wrapper.findAll('button').find(b => b.text() === 'Save')!
    await saveBtn.trigger('click')
    await flushPromises()

    const call = mockUpdateLeagueScoringSettings.mock.calls[0][1]
    expect(call.kills).toBe(4) // rounded
    expect(call.deaths).toBe(-1) // unchanged, already integer
  })
})
