from dataclasses import dataclass


@dataclass
class PlayerSearchParameters:
    summoner_name: str = None
    role: str = None
    team_id: int = None


@dataclass
class GameSearchParameters:
    state: str = None
    match_id: int = None


@dataclass
class MatchSearchParameters:
    league_slug: str = None
    tournament_id: int = None


@dataclass
class LeagueSearchParameters:
    name: str = None
    region: str = None


@dataclass
class TeamSearchParameters:
    slug: str = None
    name: str = None
    code: str = None
    status: str = None
    league: str = None


@dataclass
class TournamentSearchParameters:
    status: str = None
