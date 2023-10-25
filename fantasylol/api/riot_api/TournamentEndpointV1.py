from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from util.database_fetcher import get_db
from db.models import Tournament
from service.RiotTournamentService import RiotTournamentService
from exceptions.TournamentNotFoundException import TournamentNotFoundException

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
riot_tournament_service = RiotTournamentService()

@router.get("/tournament")
def get_riot_games(db: Session = Depends(get_db)):
    return db.query(Tournament).all()

@router.get("/tournament/{tournament_id}")
def get_riot_games(tournament_id: int, db: Session = Depends(get_db)):
    tournament_model = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament_model is None:
        raise TournamentNotFoundException()
    return tournament_model