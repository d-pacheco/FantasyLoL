from fastapi import APIRouter, Depends
from fastapi import Query
from typing import List

from fantasylol.service.riot_professional_player_service import RiotProfessionalPlayerService
from fantasylol.schemas.riot_data_schemas import ProfessionalPlayerSchema
from fantasylol.schemas.player_role import PlayerRole

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
professional_player_service = RiotProfessionalPlayerService()


def validate_role_parameter(role: PlayerRole = Query(None, description="Filter by players role")):
    return role


@router.get(
    path="/professional-player",
    description="Get a list of professional players based on a set of search criteria",
    tags=["Professional Players"],
    response_model=List[ProfessionalPlayerSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [ProfessionalPlayerSchema.ExampleResponse.example]
                }
            }
        }
    }
)
def get_riot_professional_players(
        summoner_name: str = Query(None, description="Filter by players summoner name"),
        role: str = Depends(validate_role_parameter),
        team_id: int = Query(None, description="Filter by players team id")):
    query_params = {
        "summoner_name": summoner_name,
        "role": role,
        "team_id": team_id
    }
    professional_players = professional_player_service.get_players(query_params)
    professional_players_response = [ProfessionalPlayerSchema(
        **player.to_dict()) for player in professional_players]
    return professional_players_response


@router.get(
    path="/professional-player/{professional_player_id}",
    description="Get professional player by their ID",
    tags=["Professional Players"],
    response_model=ProfessionalPlayerSchema,
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": ProfessionalPlayerSchema.ExampleResponse.example
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Professional Player not found"}
                }
            }
        }
    }
)
def get_professional_team_by_id(professional_player_id: str):
    professional_player = professional_player_service.get_player_by_id(professional_player_id)
    professional_player_response = ProfessionalPlayerSchema(**professional_player.to_dict())
    return professional_player_response


@router.get(
    path="/fetch-professional-players",
    description="Fetch professional players from riots servers",
    tags=["Professional Players"],
    response_model=List[ProfessionalPlayerSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [ProfessionalPlayerSchema.ExampleResponse.example]
                }
            }
        }
    })
def fetch_professional_teams_from_riot():
    professional_players = professional_player_service.fetch_and_store_professional_players()
    professional_players_response = [ProfessionalPlayerSchema(
        **player.to_dict()) for player in professional_players]
    return professional_players_response
