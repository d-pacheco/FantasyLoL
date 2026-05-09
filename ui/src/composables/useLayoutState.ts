import { ref } from 'vue'

const STORAGE_KEY = 'sidebar-collapsed'

const isCollapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')

export function useLayoutState() {
  function toggle() {
    isCollapsed.value = !isCollapsed.value
    localStorage.setItem(STORAGE_KEY, String(isCollapsed.value))
  }

  return { isCollapsed, toggle }
}
