from fastapi import APIRouter, Depends, Query
from fastapi_pagination import paginate, Page

from src.common.schemas.riot_data_schemas import (
    ProfessionalPlayer,
    PlayerRole,
    ProPlayerID,
    ProTeamID
)
from src.common.schemas.search_parameters import PlayerSearchParameters

from src.riot.service import RiotProfessionalPlayerService

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
professional_player_service = RiotProfessionalPlayerService()


def validate_role_parameter(
        role: PlayerRole = Query(None, description="Filter by players role")) -> PlayerRole:
    return role


@router.get(
    path="/professional-player",
    description="Get a list of professional players based on a set of search criteria",
    tags=["Professional Players"],
    response_model=Page[ProfessionalPlayer],
    responses={
        200: {
            "model": Page[ProfessionalPlayer]
        }
    }
)
def get_riot_professional_players(
        summoner_name: str = Query(None, description="Filter by players summoner name"),
        role: PlayerRole = Depends(validate_role_parameter),
        team_id: ProTeamID = Query(None, description="Filter by players team id")
) -> Page[ProfessionalPlayer]:
    search_params = PlayerSearchParameters(
        summoner_name=summoner_name,
        role=role,
        team_id=team_id
    )
    players = professional_player_service.get_players(search_params)
    return paginate(players)


@router.get(
    path="/professional-player/{professional_player_id}",
    description="Get professional player by their ID",
    tags=["Professional Players"],
    response_model=ProfessionalPlayer,
    responses={
        200: {
            "model": ProfessionalPlayer
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
def get_professional_team_by_id(professional_player_id: ProPlayerID) -> ProfessionalPlayer:
    return professional_player_service.get_player_by_id(professional_player_id)
