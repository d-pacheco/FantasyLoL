import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { mockUpdateDraftOrder } = vi.hoisted(() => ({
  mockUpdateDraftOrder: vi.fn(),
}))

vi.mock('../../src/api/fantasyApi', () => ({
  updateDraftOrder: mockUpdateDraftOrder,
}))

import DraftOrderTab from '../../src/components/leagues/DraftOrderTab.vue'

const draftOrder = [
  { user_id: 'u1', username: 'Alice', position: 1 },
  { user_id: 'u2', username: 'Bob', position: 2 },
  { user_id: 'u3', username: 'Charlie', position: 3 },
]

const defaultProps = {
  leagueId: 'league-1',
  draftOrder,
  editable: false,
  loading: false,
  error: '',
}

describe('DraftOrderTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows static list when editable is false', () => {
    const wrapper = mount(DraftOrderTab, { props: defaultProps })
    expect(wrapper.text()).toContain('Alice')
    expect(wrapper.text()).toContain('Bob')
    expect(wrapper.text()).toContain('Charlie')
    // No drag handles or save button
    expect(wrapper.findAll('.drag-handle').length).toBe(0)
    expect(wrapper.findAll('button').filter(b => b.text().includes('Save')).length).toBe(0)
  })

  it('shows draggable list with save button when editable is true', () => {
    const wrapper = mount(DraftOrderTab, { props: { ...defaultProps, editable: true } })
    expect(wrapper.text()).toContain('Alice')
    expect(wrapper.text()).toContain('Bob')
    expect(wrapper.findAll('.drag-handle').length).toBe(3)
    const saveBtn = wrapper.findAll('button').find(b => b.text().includes('Save'))
    expect(saveBtn).toBeTruthy()
  })

  it('calls updateDraftOrder on save', async () => {
    mockUpdateDraftOrder.mockResolvedValue(undefined)
    const wrapper = mount(DraftOrderTab, { props: { ...defaultProps, editable: true } })

    const saveBtn = wrapper.findAll('button').find(b => b.text().includes('Save'))!
    await saveBtn.trigger('click')
    await flushPromises()

    expect(mockUpdateDraftOrder).toHaveBeenCalledWith('league-1', [
      { user_id: 'u1', username: 'Alice', position: 1 },
      { user_id: 'u2', username: 'Bob', position: 2 },
      { user_id: 'u3', username: 'Charlie', position: 3 },
    ])
  })
})
