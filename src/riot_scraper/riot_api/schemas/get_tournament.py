from pydantic import BaseModel, ConfigDict
from src.common.schemas.riot_data_schemas import RiotTournamentID


class RiotTournament(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: RiotTournamentID
    slug: str
    startDate: str
    endDate: str


class TournamentLeague(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tournaments: list[RiotTournament]


class GetTournamentsData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    leagues: list[TournamentLeague]


class GetTournamentsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data: GetTournamentsData
