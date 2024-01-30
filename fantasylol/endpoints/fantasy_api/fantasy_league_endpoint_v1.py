from fastapi import APIRouter, Body, Depends

from fantasylol.auth.auth_bearer import JWTBearer
from fantasylol.schemas.fantasy_schemas import FantasyLeague, FantasyLeagueCreate
from fantasylol.service.fantasy.fantasy_league_service import FantasyLeagueService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
fantasy_league_service = FantasyLeagueService()


@router.post(
    path="/leagues",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyLeague
)
def create_fantasy_league(
        decoded_token: dict = Depends(JWTBearer()),
        fantasy_league: FantasyLeagueCreate = Body(...)):
    owner_id = decoded_token.get("user_id")
    return fantasy_league_service.create_fantasy_league(owner_id, fantasy_league)
