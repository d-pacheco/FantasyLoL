from pydantic import BaseModel, ConfigDict
from src.common.schemas.riot_data_schemas import RiotGameID, GameState


class Game(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: RiotGameID
    state: GameState
    number: int


class GamesData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    games: list[Game]


class GetGamesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data: GamesData
