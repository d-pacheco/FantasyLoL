from fastapi import APIRouter, Depends
from fastapi import Query
from typing import List

from fantasylol.service.riot_tournament_service import RiotTournamentService
from fantasylol.schemas.riot_data_schemas import TournamentSchema
from fantasylol.schemas.tournament_status import TournamentStatus

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
tournament_service = RiotTournamentService()

def validate_status_parameter(status: TournamentStatus = Query(None, description="Status of tournament")):
    return status

@router.get(
    path="/tournament",
    description="Get a list of tournaments based on a set of search criteria",
    tags=["tournaments"],
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
    tournaments = tournament_service.get_tournaments(status)
    tournaments_response = [TournamentSchema(**tournament.to_dict()) for tournament in tournaments]
    return tournaments_response

@router.get(
    path="/tournament/{tournament_id}",
    description="Get a tournament by its ID",
    tags=["tournaments"],
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
def get_riot_games(tournament_id: int):
    tournament = tournament_service.get_tournament_by_id(tournament_id)
    tournament_response = TournamentSchema(**tournament.to_dict())
    return tournament_response

@router.get(
    path="/fetch-tournaments",
    description="Fetch tournaments from riots servers",
    tags=["tournaments"],
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
def get_tournaments_from_riot():
    tournaments = tournament_service.fetch_and_store_tournaments()
    tournaments_response = [TournamentSchema(**tournament.to_dict) for tournament in tournaments]
    return tournaments_response
