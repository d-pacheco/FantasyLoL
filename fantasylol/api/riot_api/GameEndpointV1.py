from fastapi import APIRouter, Depends
from fastapi import Query

from fantasylol.exceptions.InvalidQueryStringParameterException import InvalidQueryStringParamterException
from fantasylol.service.RiotGameService import RiotGameService
from fantasylol.util.game_state import GameState

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
game_service = RiotGameService()

def validate_status_parameter(status: str = Query(None, description="Filter by game status")):
    allowed_statuses = [
        GameState.COMPLETED,
        GameState.INPROGRESS,
        GameState.UNSTARTED
    ]
    if status is not None and status not in allowed_statuses:
        raise InvalidQueryStringParamterException(f"Invalid status value. Must be one of '{GameState.COMPLETED}', '{GameState.INPROGRESS}' or '{GameState.UNSTARTED}'")
    return status

@router.get("/game")
def get_riot_games(
        status: str = Depends(validate_status_parameter),
        block: str = Query(None, description="Filter by game block name"),
        tournament: str = Query(None, description="Filter by game tournament id")):
    query_params = {
        "status": status,
        "block_name": block,
        "tournament_id": tournament
    }
    return game_service.get_games(query_params)

@router.get("/game/{game_id}")
def get_riot_game_by_id(game_id: int):
    return game_service.get_game_by_id(game_id)
