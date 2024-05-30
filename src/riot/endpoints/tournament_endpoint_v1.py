from fastapi import APIRouter, Depends, Query
from fastapi_pagination import paginate, Page

from ...common.schemas.riot_data_schemas import Tournament
from ...common.schemas.riot_data_schemas import TournamentStatus
from ...common.schemas.search_parameters import TournamentSearchParameters

from ..service.riot_tournament_service import RiotTournamentService

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
tournament_service = RiotTournamentService()


def validate_status_parameter(status: TournamentStatus = Query(
        None, description="Status of tournament")) -> TournamentStatus:
    return status


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
        status: TournamentStatus = Depends(validate_status_parameter)) -> Page[Tournament]:
    search_parameters = TournamentSearchParameters(status=status)
    tournaments = tournament_service.get_tournaments(search_parameters)
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
def get_riot_tournaments_by_id(tournament_id: str) -> Tournament:
    return tournament_service.get_tournament_by_id(tournament_id)
