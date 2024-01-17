from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional


class PlayerSearchParameters(BaseModel):
    summoner_name: Optional[str] = None
    role: Optional[str] = None
    team_id: Optional[str] = None


@dataclass
class GameSearchParameters:
    state: str = None
    match_id: str = None


@dataclass
class MatchSearchParameters:
    league_slug: str = None
    tournament_id: str = None


@dataclass
class LeagueSearchParameters:
    name: str = None
    region: str = None


class TeamSearchParameters(BaseModel):
    slug: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    status: Optional[str] = None
    league: Optional[str] = None


class TournamentSearchParameters(BaseModel):
    status: Optional[str] = None
