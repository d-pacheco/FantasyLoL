from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional


@dataclass
class PlayerSearchParameters:
    summoner_name: str = None
    role: str = None
    team_id: str = None


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


@dataclass
class TournamentSearchParameters:
    status: str = None
