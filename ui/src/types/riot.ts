export interface League {
  id: string
  slug: string
  name: string
  region: string
  image: string
  priority: number
  fantasy_available: boolean
}

export interface Tournament {
  id: string
  slug: string
  start_date: string
  end_date: string
  league_id: string
}

export type MatchState = 'completed' | 'inProgress' | 'unstarted'

export interface Match {
  id: string
  start_time: string
  block_name: string
  league_slug: string
  strategy_type: string
  strategy_count: number
  tournament_id: string | null
  team_1_name: string | null
  team_2_name: string | null
  has_games: boolean
  state: MatchState
  team_1_wins: number | null
  team_2_wins: number | null
  winning_team: string | null
  team_1_image: string | null
  team_2_image: string | null
}

export interface ProfessionalTeam {
  id: string
  slug: string
  name: string
  code: string
  image: string
  alternative_image: string | null
  background_image: string | null
  status: string
  home_league_name: string | null
  home_league_region: string | null
}

export type PlayerRole = 'top' | 'jungle' | 'mid' | 'bottom' | 'support' | 'none'

export interface ProfessionalPlayer {
  id: string
  summoner_name: string
  first_name: string
  last_name: string
  image: string
  role: PlayerRole
  team_id: string
  team_name: string | null
  team_code: string | null
  league_name: string | null
}

export interface PlayerGameData {
  game_id: string
  player_id: string
  participant_id: number
  champion_id: string
  role: PlayerRole
  kills: number
  deaths: number
  assists: number
  total_gold: number
  creep_score: number
  kill_participation: number
  champion_damage_share: number
  wards_placed: number
  wards_destroyed: number
}

export interface PlayerMatchHistoryEntry {
  game_id: string
  player_id: string
  match_id: string | null
  participant_id: number | null
  champion_id: string | null
  role: PlayerRole | null
  kills: number
  deaths: number
  assists: number
  total_gold: number
  creep_score: number
  kill_participation: number
  champion_damage_share: number
  wards_placed: number
  wards_destroyed: number
  start_time: string | null
  block_name: string | null
  league_slug: string | null
  patch_version: string | null
  duration_seconds: number | null
  side: string | null
  opponent_code: string | null
  opponent_name: string | null
  win: boolean | null
  multi_kills: string[]
  cs_per_min: number | null
  gold_per_min: number | null
}

export interface PlayerCareerSummary {
  player_id: string
  games_played: number
  avg_kills: number
  avg_deaths: number
  avg_assists: number
  kda_ratio: number
  avg_creep_score: number
  cs_per_min: number
  avg_total_gold: number
  gold_per_min: number
  avg_kill_participation: number
  avg_damage_share: number
  avg_wards_placed: number
  avg_wards_destroyed: number
  win_rate: number
  double_kills: number
  triple_kills: number
  quadra_kills: number
  penta_kills: number
}
