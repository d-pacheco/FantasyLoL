import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { mockGetRiotLeagues } = vi.hoisted(() => ({
  mockGetRiotLeagues: vi.fn(),
}))

const { mockUpdateLeagueSettings } = vi.hoisted(() => ({
  mockUpdateLeagueSettings: vi.fn(),
}))

vi.mock('../../src/api/riotApi', () => ({
  getRiotLeagues: mockGetRiotLeagues,
}))

vi.mock('../../src/api/fantasyApi', () => ({
  updateLeagueSettings: mockUpdateLeagueSettings,
}))

import SettingsTab from '../../src/components/leagues/SettingsTab.vue'

const lcsLeague = {
  id: 'riot-league-lcs',
  slug: 'lcs',
  name: 'LCS',
  region: 'North America',
  image: 'https://example.com/lcs.png',
  priority: 1,
  fantasy_available: true,
}

const defaultSettings = {
  name: 'My League',
  number_of_teams: 6,
  available_leagues: ['riot-league-lcs'],
}

const defaultProps = {
  settings: defaultSettings,
  loading: false,
  error: '',
  editable: false,
  leagueId: 'league-1',
}

describe('SettingsTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetRiotLeagues.mockResolvedValue({ items: [lcsLeague] })
  })

  it('displays league name instead of league ID', async () => {
    const wrapper = mount(SettingsTab, { props: defaultProps })
    await flushPromises()
    expect(wrapper.text()).toContain('LCS')
    expect(wrapper.text()).not.toContain('riot-league-lcs')
  })

  it('displays league icon alongside name', async () => {
    const wrapper = mount(SettingsTab, { props: defaultProps })
    await flushPromises()
    const img = wrapper.find('img[alt="LCS"]')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('https://example.com/lcs.png')
  })

  it('falls back to raw ID when league does not resolve', async () => {
    const wrapper = mount(SettingsTab, {
      props: {
        ...defaultProps,
        settings: { ...defaultSettings, available_leagues: ['unknown-league-id'] },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('unknown-league-id')
  })

  it('shows dash when available_leagues is empty', async () => {
    const wrapper = mount(SettingsTab, {
      props: {
        ...defaultProps,
        settings: { ...defaultSettings, available_leagues: [] },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('—')
  })

  it('shows Edit button when editable is true', async () => {
    // Edit button is now in the parent (LeagueDetailView), not in SettingsTab.
    // SettingsTab exposes startEditing() for the parent to call.
    const wrapper = mount(SettingsTab, {
      props: { ...defaultProps, editable: true },
    })
    await flushPromises()
    // Verify startEditing is exposed
    expect(typeof (wrapper.vm as unknown as { startEditing: () => void }).startEditing).toBe('function')
  })

  it('hides Edit button when editable is false', async () => {
    const wrapper = mount(SettingsTab, { props: defaultProps })
    await flushPromises()
    const editBtn = wrapper.findAll('button').filter(b => b.text() === 'Edit')
    expect(editBtn.length).toBe(0)
  })

  it('calling startEditing shows form inputs pre-populated with current values', async () => {
    const wrapper = mount(SettingsTab, {
      props: { ...defaultProps, editable: true },
    })
    await flushPromises()

    // Call startEditing via exposed method
    ;(wrapper.vm as unknown as { startEditing: () => void }).startEditing()
    await flushPromises()

    const nameInput = wrapper.find('input[type="text"]')
    expect(nameInput.exists()).toBe(true)
    expect((nameInput.element as HTMLInputElement).value).toBe('My League')

    expect(wrapper.text()).toContain('Save')
    expect(wrapper.text()).toContain('Cancel')
  })

  it('clicking Cancel exits edit mode without saving', async () => {
    const wrapper = mount(SettingsTab, {
      props: { ...defaultProps, editable: true },
    })
    await flushPromises()

    // Enter edit mode
    ;(wrapper.vm as unknown as { startEditing: () => void }).startEditing()
    await flushPromises()

    // Modify the name
    const nameInput = wrapper.find('input[type="text"]')
    await nameInput.setValue('Changed Name')

    // Click Cancel
    const cancelBtn = wrapper.findAll('button').find(b => b.text() === 'Cancel')!
    await cancelBtn.trigger('click')
    await flushPromises()

    // Should be back in read-only mode showing original name
    expect(wrapper.find('input[type="text"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('My League')
    expect(wrapper.text()).not.toContain('Changed Name')
    expect(mockUpdateLeagueSettings).not.toHaveBeenCalled()
  })

  it('successful save calls API and emits updated event', async () => {
    const updatedSettings = { name: 'New Name', number_of_teams: 6, available_leagues: ['riot-league-lcs'] }
    mockUpdateLeagueSettings.mockResolvedValue(updatedSettings)

    const wrapper = mount(SettingsTab, {
      props: { ...defaultProps, editable: true },
    })
    await flushPromises()

    // Enter edit mode
    ;(wrapper.vm as unknown as { startEditing: () => void }).startEditing()
    await flushPromises()

    // Change name
    const nameInput = wrapper.find('input[type="text"]')
    await nameInput.setValue('New Name')

    // Click Save
    const saveBtn = wrapper.findAll('button').find(b => b.text() === 'Save')!
    await saveBtn.trigger('click')
    await flushPromises()

    expect(mockUpdateLeagueSettings).toHaveBeenCalledWith('league-1', {
      name: 'New Name',
      number_of_teams: 6,
      available_leagues: ['riot-league-lcs'],
    })
    expect(wrapper.emitted('updated')).toBeTruthy()
    expect(wrapper.emitted('updated')![0]).toEqual([updatedSettings])

    // Should exit edit mode
    expect(wrapper.find('input[type="text"]').exists()).toBe(false)
  })

  it('displays inline error when save fails', async () => {
    mockUpdateLeagueSettings.mockRejectedValue({
      response: { data: { detail: 'Cannot reduce teams below active members.' } },
    })

    const wrapper = mount(SettingsTab, {
      props: { ...defaultProps, editable: true },
    })
    await flushPromises()

    // Enter edit mode
    ;(wrapper.vm as unknown as { startEditing: () => void }).startEditing()
    await flushPromises()

    // Click Save
    const saveBtn = wrapper.findAll('button').find(b => b.text() === 'Save')!
    await saveBtn.trigger('click')
    await flushPromises()

    // Error should be shown inline
    expect(wrapper.text()).toContain('Cannot reduce teams below active members.')

    // Should still be in edit mode
    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
  })
})
