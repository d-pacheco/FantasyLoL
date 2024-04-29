from fastapi import APIRouter, Depends

from src.auth.auth_bearer import JWTBearer
from src.common.schemas.fantasy_schemas import FantasyTeam
from src.fantasy.service.fantasy_team_service import FantasyTeamService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
fantasy_team_service = FantasyTeamService()


@router.put(
    path="/teams/{fantasy_league_id}/draft/{player_id}",
    tags=["Fantasy Teams"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyTeam
)
def draft_player(
        fantasy_league_id: str,
        player_id: str,
        decoded_token: dict = Depends(JWTBearer())):
    user_id = decoded_token.get("user_id")
    return fantasy_team_service.draft_player(fantasy_league_id, user_id, player_id)


@router.put(
    path="/teams/{fantasy_league_id}/drop/{player_id}",
    tags=["Fantasy Teams"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyTeam
)
def drop_player(
        fantasy_league_id: str,
        player_id: str,
        decoded_token: dict = Depends(JWTBearer())):
    user_id = decoded_token.get("user_id")
    return fantasy_team_service.drop_player(fantasy_league_id, user_id, player_id)


@router.put(
    path="/teams/{fantasy_league_id}/swap/{player_to_drop_id}/{player_to_pickup_id}",
    tags=["Fantasy Teams"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyTeam
)
def swap_players(
        fantasy_league_id: str,
        player_to_drop_id: str,
        player_to_pickup_id: str,
        decoded_token: dict = Depends(JWTBearer())):
    user_id = decoded_token.get("user_id")
    return fantasy_team_service.swap_players(
        fantasy_league_id, user_id, player_to_drop_id, player_to_pickup_id
    )
