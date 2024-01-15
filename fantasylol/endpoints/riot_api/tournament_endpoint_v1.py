from fastapi import APIRouter, Depends
from fastapi import Query
from typing import List

from fantasylol.service.riot_tournament_service import RiotTournamentService
from fantasylol.schemas.riot_data_schemas import TournamentSchema
from fantasylol.schemas.tournament_status import TournamentStatus
from fantasylol.schemas.search_parameters import TournamentSearchParameters

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
tournament_service = RiotTournamentService()


def validate_status_parameter(status: TournamentStatus = Query(
        None, description="Status of tournament")):
    return status


@router.get(
    path="/tournament",
    description="Get a list of tournaments based on a set of search criteria",
    tags=["Tournaments"],
    response_model=List[TournamentSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [TournamentSchema.ExampleResponse.example]
                }
            }
        }
    }
)
def get_riot_tournaments(status: TournamentStatus = Depends(validate_status_parameter)):
    search_parameters = TournamentSearchParameters(status=status)
    return tournament_service.get_tournaments(search_parameters)


@router.get(
    path="/tournament/{tournament_id}",
    description="Get a tournament by its ID",
    tags=["Tournaments"],
    response_model=TournamentSchema,
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": TournamentSchema.ExampleResponse.example
                }
            }
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
def get_riot_tournaments_by_id(tournament_id: str):
    return tournament_service.get_tournament_by_id(tournament_id)


@router.get(
    path="/fetch-tournaments",
    description="Fetch tournaments from riots servers",
    tags=["Tournaments"],
    response_model=List[TournamentSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [TournamentSchema.ExampleResponse.example]
                }
            }
        }
    }
)
def fetch_tournaments_from_riot():
    return tournament_service.fetch_and_store_tournaments()
