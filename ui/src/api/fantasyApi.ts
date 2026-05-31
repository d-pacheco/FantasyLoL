import { api } from './client'
import type { FantasyLeague, FantasyLeagueSettings, FantasyLeagueScoringSettings, DraftState, PickRequest } from '../types/fantasy'
import type { ProfessionalPlayer, ProfessionalTeam } from '../types/riot'

export interface MyLeaguesResponse {
  pending: FantasyLeague[]
  accepted: FantasyLeague[]
}

export interface LeagueMember {
  user_id: string
  username: string
  status: 'accepted' | 'pending'
}

export interface DraftOrderEntry {
  user_id: string
  username: string
  position: number
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

export async function getLeagueById(leagueId: string): Promise<FantasyLeague> {
  const res = await api.get<FantasyLeague>(`/fantasy/leagues/${leagueId}`)
  return res.data
}

export async function getLeagueMembers(leagueId: string): Promise<LeagueMember[]> {
  const res = await api.get<LeagueMember[]>(`/fantasy/leagues/${leagueId}/members`)
  return res.data
}

export async function getLeagueSettings(leagueId: string): Promise<FantasyLeagueSettings> {
  const res = await api.get<FantasyLeagueSettings>(`/fantasy/leagues/${leagueId}/settings`)
  return res.data
}

export async function getLeagueScoringSettings(leagueId: string): Promise<FantasyLeagueScoringSettings> {
  const res = await api.get<FantasyLeagueScoringSettings>(`/fantasy/leagues/${leagueId}/scoring`)
  return res.data
}

export async function getDraftOrder(leagueId: string): Promise<DraftOrderEntry[]> {
  const res = await api.get<DraftOrderEntry[]>(`/fantasy/leagues/${leagueId}/draft-order`)
  return res.data
}

export async function updateDraftOrder(leagueId: string, order: DraftOrderEntry[]): Promise<void> {
  await api.put(`/fantasy/leagues/${leagueId}/draft-order`, order)
}

export async function inviteToLeague(leagueId: string, username: string): Promise<void> {
  await api.post(`/fantasy/leagues/${leagueId}/invite/${username}`)
}

export async function startDraft(leagueId: string): Promise<void> {
  await api.post(`/fantasy/leagues/${leagueId}/draft/start`)
}

export async function getDraftState(leagueId: string): Promise<DraftState> {
  const res = await api.get<DraftState>(`/fantasy/leagues/${leagueId}/draft/state`)
  return res.data
}

export async function getAvailablePlayers(leagueId: string): Promise<ProfessionalPlayer[]> {
  const res = await api.get<ProfessionalPlayer[]>(`/fantasy/leagues/${leagueId}/draft/available-players`)
  return res.data
}

export async function getAvailableTeams(leagueId: string): Promise<ProfessionalTeam[]> {
  const res = await api.get<ProfessionalTeam[]>(`/fantasy/leagues/${leagueId}/draft/available-teams`)
  return res.data
}

export async function makePick(leagueId: string, request: PickRequest): Promise<void> {
  await api.post(`/fantasy/leagues/${leagueId}/draft/pick`, request)
}
