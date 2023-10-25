from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from sqlalchemy.orm import Session
from util.database_fetcher import get_db
from db.models import ProfessionalTeam
from exceptions.ProfessionalTeamNotFoundException import ProfessionalTeamNotFoundException

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")

@router.get("/professional-team")
def get_riot_professional_teams(
        slug: str = Query(None, description="Filter by professional teams slug"),
        name: str = Query(None, description="Filter by professional teams name"),
        code: str = Query(None, description="Filter by professional teams code"),
        status: str = Query(None, description="Filter by professional teams status"),
        league: str = Query(None, description="Filter by professional teams home league"),
        db: Session = Depends(get_db)):
    query = db.query(ProfessionalTeam)

    if slug:
        query = query.filter(ProfessionalTeam.slug == slug)
    if name:
        query = query.filter(ProfessionalTeam.name == name)
    if code:
        query = query.filter(ProfessionalTeam.code == code)
    if status:
        query = query.filter(ProfessionalTeam.status == status)
    if league:
        query = query.filter(ProfessionalTeam.home_league == league)
    return query.all()

@router.get("/professional-team/{professional_team_id}")
def get_riot_league_by_id(professional_team_id: int, db: Session = Depends(get_db)):
    professional_team_model = db.query(ProfessionalTeam).filter(ProfessionalTeam.id == professional_team_id).first()
    if professional_team_model is None:
        raise ProfessionalTeamNotFoundException()
    return professional_team_model
