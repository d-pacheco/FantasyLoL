import { api, type PaginatedResponse } from './client'
import type { ProfessionalPlayer, ProfessionalTeam, Match } from '../types/riot'

export interface PlayerParams {
  page?: number
  size?: number
  summoner_name?: string
  role?: string
  team_name?: string
  fantasy_available?: boolean
}

export interface TeamParams {
  page?: number
  size?: number
  name?: string
  code?: string
  status?: string
}

export interface MatchParams {
  page?: number
  size?: number
  league_slug?: string
  tournament_id?: string
}

export async function getPlayers(params: PlayerParams = {}): Promise<PaginatedResponse<ProfessionalPlayer>> {
  const res = await api.get<PaginatedResponse<ProfessionalPlayer>>('/professional-player', { params })
  return res.data
}

export async function getTeams(params: TeamParams = {}): Promise<PaginatedResponse<ProfessionalTeam>> {
  const res = await api.get<PaginatedResponse<ProfessionalTeam>>('/professional-team', { params })
  return res.data
}

export async function getMatches(params: MatchParams = {}): Promise<PaginatedResponse<Match>> {
  const res = await api.get<PaginatedResponse<Match>>('/match', { params })
  return res.data
}
