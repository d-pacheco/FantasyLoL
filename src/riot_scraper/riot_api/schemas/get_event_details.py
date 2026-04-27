from pydantic import BaseModel, ConfigDict
from src.common.schemas.riot_data_schemas import (
    RiotGameID,
    GameState,
    RiotTournamentID,
    RiotLeagueID,
    ProTeamID,
    RiotMatchID,
)


class EventTournament(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: RiotTournamentID


class EventLeague(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: RiotLeagueID
    slug: str
    image: str
    name: str


class MatchStrategy(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    count: int


class TeamResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    gameWins: int


class MatchTeam(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: ProTeamID
    name: str
    code: str
    image: str
    result: TeamResult


class GameTeam(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: ProTeamID
    side: str


class MatchGame(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    number: int
    id: RiotGameID
    state: GameState
    teams: list[GameTeam]


class EventMatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    strategy: MatchStrategy
    teams: list[MatchTeam]
    games: list[MatchGame]


class Event(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: RiotMatchID
    type: str
    tournament: EventTournament
    league: EventLeague
    match: EventMatch


class EventData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event: Event


class EventDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data: EventData
