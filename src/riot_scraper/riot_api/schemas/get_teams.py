from pydantic import BaseModel, ConfigDict
from src.common.schemas.riot_data_schemas import ProTeamID, ProPlayerID, PlayerRole


class HomeLeague(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    region: str


class TeamPlayer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: ProPlayerID
    summonerName: str
    firstName: str
    lastName: str
    image: str
    role: PlayerRole


class Team(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: ProTeamID
    slug: str
    name: str
    code: str
    image: str
    alternativeImage: str | None
    backgroundImage: str | None
    status: str
    homeLeague: HomeLeague | None
    players: list[TeamPlayer]


class TeamData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    teams: list[Team]


class GetTeamsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data: TeamData
