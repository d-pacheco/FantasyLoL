import type { PlayerRole } from './riot'

export type FantasyLeagueStatus = 'pre-draft' | 'draft' | 'active' | 'completed' | 'deleted'

export interface FantasyLeagueSettings {
  name: string
  number_of_teams: number
  available_leagues: string[]
}

export interface FantasyLeague extends FantasyLeagueSettings {
  id: string
  owner_id: string
  status: FantasyLeagueStatus
  current_week: number | null
  current_draft_position: number | null
}

export interface FantasyLeagueScoringSettings {
  fantasy_league_id: string | null
  kills: number
  deaths: number
  assists: number
  cspm: number
  wards_placed: number
  wards_destroyed: number
  kill_participation: number
  damage_percentage: number
  double_kill: number
  triple_kill: number
  quadra_kill: number
  penta_kill: number
  match_win: number
  match_sweep: number
  dragon: number
  elder_dragon: number
  baron: number
  tower: number
  inhibitor: number
  soul: number
}

export interface FantasyTeam {
  fantasy_league_id: string
  user_id: string
  week: number
  top_player_id: string | null
  jungle_player_id: string | null
  mid_player_id: string | null
  adc_player_id: string | null
  support_player_id: string | null
  team_id: string | null
}

export interface RosterEntry {
  player_id: string
  summoner_name: string
  role: PlayerRole
  team_code: string
  points: number
  trend: 'up' | 'down' | 'neutral'
}

export interface LeaderboardEntry {
  user_id: string
  username: string
  position: number
  points: number
  is_current_user: boolean
}

export interface LiveMatch {
  match_id: string
  team_1_name: string
  team_2_name: string
  team_1_score: number
  team_2_score: number
  league_slug: string
  start_time: string
}

export interface ActivityEvent {
  id: string
  type: 'score' | 'trade' | 'pickup' | 'drop'
  description: string
  timestamp: string
}

export interface DraftPick {
  fantasy_league_id: string
  pick_number: number
  round_number: number
  user_id: string
  player_id: string | null
  team_id: string | null
}

export interface UserSlots {
  top_player_id: string | null
  jungle_player_id: string | null
  mid_player_id: string | null
  adc_player_id: string | null
  support_player_id: string | null
  team_id: string | null
}

export interface DraftState {
  fantasy_league_id: string
  current_round: number
  current_pick_number: number
  total_picks: number
  current_turn_user_id: string | null
  picks: DraftPick[]
  user_slots: Record<string, UserSlots>
  is_complete: boolean
}

export interface PickRequest {
  player_id?: string
  team_id?: string
}

export interface PickMadeEvent {
  event: 'pick_made'
  pick: DraftPick
  next_turn_user_id: string | null
}

export interface DraftCompletedEvent {
  event: 'draft_completed'
}

export type DraftEvent = PickMadeEvent | DraftCompletedEvent
