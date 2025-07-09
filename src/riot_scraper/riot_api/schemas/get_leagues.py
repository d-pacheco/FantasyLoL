from pydantic import BaseModel, ConfigDict
from src.common.schemas.riot_data_schemas import RiotLeagueID


class DisplayPriority(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    position: int
    status: str


class League(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: RiotLeagueID
    slug: str
    name: str
    region: str
    image: str
    displayPriority: DisplayPriority


class LeagueData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    leagues: list[League]


class GetLeaguesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data: LeagueData
