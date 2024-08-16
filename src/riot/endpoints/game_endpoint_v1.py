import logging
from fastapi import APIRouter, Depends, Query
from fastapi_pagination import paginate, Page

from src.common.schemas.riot_data_schemas import Game, GameState, RiotGameID, RiotMatchID
from src.common.schemas.search_parameters import GameSearchParameters
from src.db.database_config import DatabaseConfig
from src.db.database_connection_provider import DatabaseConnectionProvider
from src.db.database_service import DatabaseService

from src.riot.service import RiotGameService

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
game_service = RiotGameService(DatabaseService(
    DatabaseConnectionProvider(
        DatabaseConfig(database_url="sqlite:///./fantasy-league-of-legends.db")
    )
))
logger = logging.getLogger('fantasy-lol')


def validate_status_parameter(state: GameState = Query(None, description="Filter by game state")):
    return state


@router.get(
    path="/game",
    description="Get a list of games based on a set of search criteria",
    tags=["Games"],
    response_model=Page[Game],
    responses={
        200: {
            "model": Page[Game]
        }
    }
)
def get_riot_games(
        state: GameState = Depends(validate_status_parameter),
        match_id: RiotMatchID = Query(None, description="Filter by game match id")) -> Page[Game]:
    search_parameters = GameSearchParameters(
        state=state,
        match_id=match_id
    )
    games = game_service.get_games(search_parameters)
    return paginate(games)


@router.get(
    path="/game/{game_id}",
    description="Get game by its ID",
    tags=["Games"],
    response_model=Game,
    responses={
        200: {
            "model": Game
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Game not found"}
                }
            }
        }
    }
)
def get_riot_game_by_id(game_id: RiotGameID) -> Game:
    return game_service.get_game_by_id(game_id)
