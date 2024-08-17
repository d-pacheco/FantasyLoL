from fastapi import APIRouter, Depends, Query
from fastapi_pagination import paginate, Page

from src.common.schemas.riot_data_schemas import Tournament, TournamentStatus, RiotTournamentID
from src.common.schemas.search_parameters import TournamentSearchParameters
from src.db.database_service import db_service

from src.riot.service import RiotTournamentService

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
tournament_service = RiotTournamentService(db_service)


def validate_status_parameter(status: TournamentStatus = Query(
        None, description="Status of tournament")):
    return status


def get_tournament_service() -> RiotTournamentService:
    return tournament_service


@router.get(
    path="/tournament",
    description="Get a list of tournaments based on a set of search criteria",
    tags=["Tournaments"],
    response_model=Page[Tournament],
    responses={
        200: {
            "model": Page[Tournament]
        }
    }
)
def get_riot_tournaments(
        status: TournamentStatus = Depends(validate_status_parameter),
        service: RiotTournamentService = Depends(get_tournament_service)
) -> Page[Tournament]:
    search_parameters = TournamentSearchParameters(status=status)
    tournaments = service.get_tournaments(search_parameters)
    return paginate(tournaments)


@router.get(
    path="/tournament/{tournament_id}",
    description="Get a tournament by its ID",
    tags=["Tournaments"],
    response_model=Tournament,
    responses={
        200: {
            "model": Tournament
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Tournament not found"}
                }
            }
        }
    }
)
def get_riot_tournaments_by_id(
        tournament_id: RiotTournamentID,
        service: RiotTournamentService = Depends(get_tournament_service)
) -> Tournament:
    return service.get_tournament_by_id(tournament_id)
