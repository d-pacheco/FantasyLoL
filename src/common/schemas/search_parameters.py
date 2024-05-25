from pydantic import BaseModel
from typing import Optional


class PlayerSearchParameters(BaseModel):
    summoner_name: Optional[str] = None
    role: Optional[str] = None
    team_id: Optional[str] = None


class GameSearchParameters(BaseModel):
    state: Optional[str] = None
    match_id: Optional[str] = None


class PlayerGameStatsSearchParameters(BaseModel):
    game_id: Optional[str] = None
    player_id: Optional[str] = None


class MatchSearchParameters(BaseModel):
    league_slug: Optional[str] = None
    tournament_id: Optional[str] = None


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
    status: Optional[str] = None
