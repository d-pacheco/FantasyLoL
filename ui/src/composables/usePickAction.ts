import { ref, computed, toValue, watch } from 'vue'
import type { MaybeRefOrGetter } from 'vue'
import axios from 'axios'
import { makePick } from '../api/fantasyApi'

export function usePickAction(leagueId: string, options: { isMyTurn: MaybeRefOrGetter<boolean> }) {
  const pickInProgress = ref(false)
  const pickError = ref<string | null>(null)

  const pickDisabled = computed(() => !toValue(options.isMyTurn) || pickInProgress.value)

  // Reset pickInProgress when the turn rotates back to us via WebSocket
  watch(() => toValue(options.isMyTurn), (isMyTurn) => {
    if (isMyTurn) pickInProgress.value = false
  })

  async function pick(playerId: string): Promise<void> {
    pickInProgress.value = true
    pickError.value = null
    try {
      await makePick(leagueId, { player_id: playerId })
    } catch (e) {
      const detail = axios.isAxiosError(e) ? e.response?.data?.detail : null
      pickError.value = detail ?? 'Pick failed. Please try again.'
      pickInProgress.value = false
    }
  }

  async function pickTeam(teamId: string): Promise<void> {
    pickInProgress.value = true
    pickError.value = null
    try {
      await makePick(leagueId, { team_id: teamId })
    } catch (e) {
      const detail = axios.isAxiosError(e) ? e.response?.data?.detail : null
      pickError.value = detail ?? 'Pick failed. Please try again.'
      pickInProgress.value = false
    }
  }

  return { pickDisabled, pickInProgress, pickError, pick, pickTeam }
}
