import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DraftCompleteModal from '../../src/components/draft/DraftCompleteModal.vue'

describe('DraftCompleteModal', () => {
  it('is not visible when show is false', () => {
    const wrapper = mount(DraftCompleteModal, { props: { show: false } })
    expect(wrapper.find('[data-testid="modal"]').exists()).toBe(false)
  })

  it('shows "Draft Complete!" when show is true', () => {
    const wrapper = mount(DraftCompleteModal, { props: { show: true } })
    expect(wrapper.find('[data-testid="modal"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Draft Complete!')
  })

  it('emits goToLeague when button is clicked', async () => {
    const wrapper = mount(DraftCompleteModal, { props: { show: true } })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('goToLeague')).toBeTruthy()
  })
})
