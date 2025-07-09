from pydantic import BaseModel, ConfigDict
from src.common.schemas.riot_data_schemas import RiotMatchID, MatchState


class Pages(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    older: str | None
    newer: str | None


class ScheduleLeague(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    slug: str


class MatchStrategy(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
    count: int


class MatchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    outcome: str | None
    gameWins: int


class TeamRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    wins: int
    losses: int


class MatchTeam(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    code: str
    image: str
    result: MatchResult | None
    record: TeamRecord | None


class ScheduleMatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: RiotMatchID
    teams: list[MatchTeam]
    strategy: MatchStrategy


class ScheduleEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    startTime: str
    state: MatchState
    type: str
    blockName: str
    league: ScheduleLeague
    match: ScheduleMatch


class Schedule(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pages: Pages
    events: list[ScheduleEvent]


class ScheduleData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schedule: Schedule


class GetScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data: ScheduleData
