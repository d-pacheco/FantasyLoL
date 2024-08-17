from fastapi import APIRouter, Depends
from typing import List

from src.auth import JWTBearer

from src.common.schemas.fantasy_schemas import FantasyTeam, FantasyLeagueID, UserID
from src.common.schemas.riot_data_schemas import ProPlayerID
from src.db.database_service import db_service

from src.fantasy.service import FantasyTeamService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
fantasy_team_service = FantasyTeamService(db_service)


def get_fantasy_team_service() -> FantasyTeamService:
    return fantasy_team_service


@router.get(
    path="/teams/{fantasy_league_id}",
    tags=["Fantasy Teams"],
    dependencies=[Depends(JWTBearer())],
    response_model=List[FantasyTeam]
)
def get_fantasy_team_weeks_for_league(
        fantasy_league_id: FantasyLeagueID,
        decoded_token: dict = Depends(JWTBearer()),
        service: FantasyTeamService = Depends(get_fantasy_team_service)
) -> List[FantasyTeam]:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return service.get_all_fantasy_team_weeks(fantasy_league_id, user_id)


@router.put(
    path="/teams/{fantasy_league_id}/pickup/{player_id}",
    tags=["Fantasy Teams"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyTeam
)
def pickup_player(
        fantasy_league_id: FantasyLeagueID,
        player_id: ProPlayerID,
        decoded_token: dict = Depends(JWTBearer()),
        service: FantasyTeamService = Depends(get_fantasy_team_service)
) -> FantasyTeam:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return service.pickup_player(fantasy_league_id, user_id, player_id)


@router.put(
    path="/teams/{fantasy_league_id}/drop/{player_id}",
    tags=["Fantasy Teams"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyTeam
)
def drop_player(
        fantasy_league_id: FantasyLeagueID,
        player_id: ProPlayerID,
        decoded_token: dict = Depends(JWTBearer()),
        service: FantasyTeamService = Depends(get_fantasy_team_service)
) -> FantasyTeam:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return service.drop_player(fantasy_league_id, user_id, player_id)


@router.put(
    path="/teams/{fantasy_league_id}/swap/{player_to_drop_id}/{player_to_pickup_id}",
    tags=["Fantasy Teams"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyTeam
)
def swap_players(
        fantasy_league_id: FantasyLeagueID,
        player_to_drop_id: ProPlayerID,
        player_to_pickup_id: ProPlayerID,
        decoded_token: dict = Depends(JWTBearer()),
        service: FantasyTeamService = Depends(get_fantasy_team_service)
) -> FantasyTeam:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return service.swap_players(fantasy_league_id, user_id, player_to_drop_id, player_to_pickup_id)
