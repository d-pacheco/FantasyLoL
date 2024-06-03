from pydantic import BaseModel
from typing import Optional

from .riot_data_schemas import (
    GameState,
    RiotGameID,
    RiotMatchID,
    RiotTournamentID,
    ProPlayerID,
    ProTeamID,
    PlayerRole,
    TournamentStatus
)


class PlayerSearchParameters(BaseModel):
    summoner_name: Optional[str] = None
    role: Optional[PlayerRole] = None
    team_id: Optional[ProTeamID] = None


class GameSearchParameters(BaseModel):
    state: Optional[GameState] = None
    match_id: Optional[RiotMatchID] = None


class PlayerGameStatsSearchParameters(BaseModel):
    game_id: Optional[RiotGameID] = None
    player_id: Optional[ProPlayerID] = None


class MatchSearchParameters(BaseModel):
    league_slug: Optional[str] = None
    tournament_id: Optional[RiotTournamentID] = None


class LeagueSearchParameters(BaseModel):
    name: Optional[str] = None
    region: Optional[str] = None
    fantasy_available: Optional[bool] = None


class TeamSearchParameters(BaseModel):
    slug: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    status: Optional[str] = None
    league: Optional[str] = None


class TournamentSearchParameters(BaseModel):
    status: Optional[TournamentStatus] = None
