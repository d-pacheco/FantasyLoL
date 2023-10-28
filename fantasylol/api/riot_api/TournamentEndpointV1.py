from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi import Query
from sqlalchemy.orm import Session

from exceptions.InvalidQueryStringParameterException import InvalidQueryStringParamterException
from service.RiotTournamentService import RiotTournamentService
from util.tournament_status import TournamentStatus

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
tournament_service = RiotTournamentService()

def validate_status_parameter(status: str = Query(None, description="Status of tournament")):
    allowed_statuses = [
        TournamentStatus.COMPLETED,
        TournamentStatus.ACTIVE,
        TournamentStatus.UPCOMING
    ]
    if status is not None and status not in allowed_statuses:
        raise InvalidQueryStringParamterException("Invalid status value. Must be one of 'active', 'completed' or 'upcoming'")
    return status

@router.get("/tournament")
def get_riot_games(status: str = Depends(validate_status_parameter)):
    return tournament_service.get_tournaments(status)

@router.get("/tournament/{tournament_id}")
def get_riot_games(tournament_id: int):
    return tournament_service.get_tournament_by_id(tournament_id)
