from fastapi import APIRouter
from fastapi import Query

from fantasylol.service.RiotProfessionalTeamService import RiotProfessionalTeamService

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
professional_team_service = RiotProfessionalTeamService()

@router.get("/professional-team")
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
    return professional_team_service.get_teams(query_params)

@router.get("/professional-team/{professional_team_id}")
def get_riot_league_by_id(professional_team_id: int):
    return professional_team_service.get_team_by_id(professional_team_id)

@router.get("/fetch-professional-teams")
def fetch_profressional_teams_from_riot():
    return professional_team_service.fetch_and_store_professional_teams()
