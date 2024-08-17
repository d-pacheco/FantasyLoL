from fastapi import APIRouter, Query, Depends
from fastapi_pagination import paginate, Page

from src.common.schemas.riot_data_schemas import ProfessionalTeam, ProTeamID
from src.common.schemas.search_parameters import TeamSearchParameters
from src.db.database_service import db_service

from src.riot.service import RiotProfessionalTeamService

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
professional_team_service = RiotProfessionalTeamService(db_service)


def get_team_service() -> RiotProfessionalTeamService:
    return professional_team_service


@router.get(
    path="/professional-team",
    description="Get a list of professional teams based on a set of search criteria",
    tags=["Professional Teams"],
    response_model=Page[ProfessionalTeam],
    responses={
        200: {
            "model": Page[ProfessionalTeam]
        }
    }
)
def get_riot_professional_teams(
        slug: str = Query(None, description="Filter by professional teams slug"),
        name: str = Query(None, description="Filter by professional teams name"),
        code: str = Query(None, description="Filter by professional teams code"),
        status: str = Query(None, description="Filter by professional teams status"),
        league: str = Query(None, description="Filter by professional teams home league"),
        service: RiotProfessionalTeamService = Depends(get_team_service)
) -> Page[ProfessionalTeam]:
    search_parameters = TeamSearchParameters(
        slug=slug,
        name=name,
        code=code,
        status=status,
        league=league
    )
    teams = service.get_teams(search_parameters)
    return paginate(teams)


@router.get(
    path="/professional-team/{professional_team_id}",
    description="Get professional team by its ID",
    tags=["Professional Teams"],
    response_model=ProfessionalTeam,
    responses={
        200: {
            "model": ProfessionalTeam
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
def get_professional_team_by_id(
        professional_team_id: ProTeamID,
        service: RiotProfessionalTeamService = Depends(get_team_service)
) -> ProfessionalTeam:
    return service.get_team_by_id(professional_team_id)
