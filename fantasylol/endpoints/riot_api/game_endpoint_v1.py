from fastapi import APIRouter, Depends
from fastapi import Query
from typing import List

from fantasylol.service.riot_game_service import RiotGameService
from fantasylol.schemas.riot_data_schemas import GameSchema
from fantasylol.schemas.game_state import GameState

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
game_service = RiotGameService()


def validate_status_parameter(status: GameState = Query(None, description="Filter by game state")):
    return status


@router.get(
    path="/game",
    description="Get a list of games based on a set of search criteria",
    tags=["games"],
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
        status: GameState = Depends(validate_status_parameter),
        block: str = Query(None, description="Filter by game block name"),
        tournament: str = Query(None, description="Filter by game tournament id")):
    query_params = {
        "status": status,
        "block_name": block,
        "tournament_id": tournament
    }
    games = game_service.get_games(query_params)
    games_response = [GameSchema(**game.to_dict()) for game in games]
    return games_response


@router.get(
    path="/game/{game_id}",
    description="Get game by its ID",
    tags=["games"],
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
def get_riot_game_by_id(game_id: int):
    game = game_service.get_game_by_id(game_id)
    game_response = GameSchema(**game.to_dict())
    return game_response


@router.get(
    path="/fetch-games",
    description="Fetch live games from riots servers",
    tags=["games"],
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
def fetch_live_games_from_riot():
    games = game_service.fetch_and_store_live_games()
    games_response = [GameSchema(**game.to_dict()) for game in games]
    return games_response
