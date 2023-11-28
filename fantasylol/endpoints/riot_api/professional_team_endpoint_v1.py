from fastapi import APIRouter
from fastapi import Query
from typing import List

from fantasylol.service.riot_professional_team_service import RiotProfessionalTeamService
from fantasylol.schemas.riot_data_schemas import ProfessionalTeamSchema

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
professional_team_service = RiotProfessionalTeamService()

@router.get(
    path="/professional-team",
    description="Get a list of professional teams based on a set of search criteria",
    tags=["Professional Teams"],
    response_model=List[ProfessionalTeamSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [ProfessionalTeamSchema.ExampleResponse.example]
                }
            }
        }
    }
)
def get_riot_professional_teams(
        slug: str = Query(None, description="Filter by professional teams slug"),
        name: str = Query(None, description="Filter by professional teams name"),
        code: str = Query(None, description="Filter by professional teams code"),
        status: str = Query(None, description="Filter by professional teams status"),
        league: str = Query(None, description="Filter by professional teams home league")):
    query_params = {
        "slug": slug,
        "name": name,
        "code": code,
        "status": status,
        "home_league": league
    }
    professional_teams = professional_team_service.get_teams(query_params)
    professional_teams_response = [ProfessionalTeamSchema(**team.to_dict()) for team in professional_teams]
    return professional_teams_response


@router.get(
    path="/professional-team/{professional_team_id}",
    description="Get professional team by its ID",
    tags=["Professional Teams"],
    response_model=ProfessionalTeamSchema,
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": ProfessionalTeamSchema.ExampleResponse.example
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Professional Team not found"}
                }
            }
        }
    }
)
def get_riot_league_by_id(professional_team_id: int):
    professional_team = professional_team_service.get_team_by_id(professional_team_id)
    professional_team_response = ProfessionalTeamSchema(**professional_team.to_dict())
    return professional_team_response

@router.get(
    path="/fetch-professional-teams",
    description="Fetch professional teams from riots servers",
    tags=["Professional Teams"],
    response_model=List[ProfessionalTeamSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [ProfessionalTeamSchema.ExampleResponse.example]
                }
            }
        }
    })
def fetch_profressional_teams_from_riot():
    professional_teams = professional_team_service.fetch_and_store_professional_teams()
    professional_teams_response = [ProfessionalTeamSchema(**team.to_dict()) for team in professional_teams]
    return professional_teams_response
