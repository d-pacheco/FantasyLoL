from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from sqlalchemy.orm import Session
from util.database_fetcher import get_db
from db.models import League
from exceptions.LeagueNotFoundException import LeagueNotFoundException

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")

@router.get("/league")
def get_riot_leagues(
        name: str = Query(None, description="Filter by league name"),
        region: str = Query(None, description="Filter by league region"),
        db: Session = Depends(get_db)):
    query = db.query(League)

    if name:
        query = query.filter(League.name == name)
    if region:
        query = query.filter(League.region == region)
    return query.all()

@router.get("/league/{league_id}")
def get_riot_league_by_id(league_id: int, db: Session = Depends(get_db)):
    league_model = db.query(League).filter(League.id == league_id).first()
    if league_model is None:
        raise LeagueNotFoundException()
    return league_model
