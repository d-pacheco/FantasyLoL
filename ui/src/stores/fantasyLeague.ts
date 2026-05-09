import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'selected-league-id'

export const useFantasyLeagueStore = defineStore('fantasyLeague', () => {
  const selectedLeagueId = ref<string | null>(localStorage.getItem(STORAGE_KEY))

  function selectLeague(id: string | null) {
    selectedLeagueId.value = id
    if (id) {
      localStorage.setItem(STORAGE_KEY, id)
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  return { selectedLeagueId, selectLeague }
})
