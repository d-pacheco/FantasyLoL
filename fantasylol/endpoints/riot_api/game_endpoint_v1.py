import logging
from fastapi import APIRouter, Depends
from fastapi import Query
from typing import List

from fantasylol.service.riot_game_service import RiotGameService
from fantasylol.schemas.riot_data_schemas import GameSchema
from fantasylol.schemas.game_state import GameState
from fantasylol.schemas.search_parameters import GameSearchParameters

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
game_service = RiotGameService()
logger = logging.getLogger('fantasy-lol')


def validate_status_parameter(state: GameState = Query(None, description="Filter by game state")):
    return state


@router.get(
    path="/game",
    description="Get a list of games based on a set of search criteria",
    tags=["Games"],
    response_model=List[GameSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [GameSchema.ExampleResponse.example]
                }
            }
        }
    }
)
def get_riot_games(
        state: GameState = Depends(validate_status_parameter),
        match_id: str = Query(None, description="Filter by game match id")):
    search_parameters = GameSearchParameters(
        state=state,
        match_id=match_id
    )
    return game_service.get_games(search_parameters)


@router.get(
    path="/game/{game_id}",
    description="Get game by its ID",
    tags=["Games"],
    response_model=GameSchema,
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": GameSchema.ExampleResponse.example
                }
            }
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
def get_riot_game_by_id(game_id: str):
    return game_service.get_game_by_id(game_id)


@router.get(
    path="/fetch-games-from-matches",
    description="Manually trigger fetch games from match ids job",
    tags=["Manual Job Triggers"]
)
def fetch_games_from_matches(batch_size: int = Query(None, description="size of the batches")):
    game_service.fetch_and_store_games_from_match_ids(batch_size)
