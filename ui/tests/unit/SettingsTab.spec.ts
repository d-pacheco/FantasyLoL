import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const { mockGetRiotLeagues } = vi.hoisted(() => ({
  mockGetRiotLeagues: vi.fn(),
}))

vi.mock('../../src/api/riotApi', () => ({
  getRiotLeagues: mockGetRiotLeagues,
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

describe('SettingsTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetRiotLeagues.mockResolvedValue({ items: [lcsLeague] })
  })

  it('displays league name instead of league ID', async () => {
    const wrapper = mount(SettingsTab, {
      props: {
        settings: {
          name: 'My League',
          number_of_teams: 6,
          available_leagues: ['riot-league-lcs'],
        },
        loading: false,
        error: '',
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('LCS')
    expect(wrapper.text()).not.toContain('riot-league-lcs')
  })

  it('displays league icon alongside name', async () => {
    const wrapper = mount(SettingsTab, {
      props: {
        settings: {
          name: 'My League',
          number_of_teams: 6,
          available_leagues: ['riot-league-lcs'],
        },
        loading: false,
        error: '',
      },
    })
    await flushPromises()
    const img = wrapper.find('img[alt="LCS"]')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('https://example.com/lcs.png')
  })

  it('falls back to raw ID when league does not resolve', async () => {
    mockGetRiotLeagues.mockResolvedValue({ items: [lcsLeague] })
    const wrapper = mount(SettingsTab, {
      props: {
        settings: {
          name: 'My League',
          number_of_teams: 6,
          available_leagues: ['unknown-league-id'],
        },
        loading: false,
        error: '',
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('unknown-league-id')
  })

  it('shows dash when available_leagues is empty', async () => {
    const wrapper = mount(SettingsTab, {
      props: {
        settings: {
          name: 'My League',
          number_of_teams: 6,
          available_leagues: [],
        },
        loading: false,
        error: '',
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('—')
  })
})
