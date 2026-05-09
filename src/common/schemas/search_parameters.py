from pydantic import BaseModel

from .riot_data_schemas import (
    GameState,
    RiotGameID,
    RiotMatchID,
    RiotTournamentID,
    ProPlayerID,
    PlayerRole,
    TournamentStatus,
)


class PlayerSearchParameters(BaseModel):
    summoner_name: str | None = None
    role: PlayerRole | None = None
    team_name: str | None = None
    fantasy_available: bool | None = None
    active_only: bool = True


class GameSearchParameters(BaseModel):
    state: GameState | None = None
    match_id: RiotMatchID | None = None


class PlayerGameStatsSearchParameters(BaseModel):
    game_id: RiotGameID | None = None
    player_id: ProPlayerID | None = None


class MatchSearchParameters(BaseModel):
    league_slug: str | None = None
    tournament_id: RiotTournamentID | None = None


class LeagueSearchParameters(BaseModel):
    name: str | None = None
    region: str | None = None
    fantasy_available: bool | None = None


class TeamSearchParameters(BaseModel):
    slug: str | None = None
    name: str | None = None
    code: str | None = None
    status: str | None = None
    league: str | None = None
    search: str | None = None
    fantasy_available: bool | None = None
    active_only: bool = True


class TournamentSearchParameters(BaseModel):
    status: TournamentStatus | None = None
