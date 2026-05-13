import { api } from './client'
import type { FantasyLeague, FantasyLeagueSettings } from '../types/fantasy'

export interface MyLeaguesResponse {
  pending: FantasyLeague[]
  accepted: FantasyLeague[]
}

export async function getMyLeagues(): Promise<MyLeaguesResponse> {
  const res = await api.get<MyLeaguesResponse>('/fantasy/leagues')
  return res.data
}

export async function createLeague(settings: FantasyLeagueSettings): Promise<FantasyLeague> {
  const res = await api.post<FantasyLeague>('/fantasy/leagues', settings)
  return res.data
}

export async function joinLeague(leagueId: string): Promise<void> {
  await api.post(`/fantasy/leagues/${leagueId}/join`)
}

export async function leaveLeague(leagueId: string): Promise<void> {
  await api.post(`/fantasy/leagues/${leagueId}/leave`)
}
