from fastapi import APIRouter, Body, Depends
from typing import List

from src.auth.auth_bearer import JWTBearer
from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueSettings,
    FantasyLeagueScoringSettings,
    FantasyLeagueDraftOrderResponse
)
from src.fantasy.service.fantasy_league_service import FantasyLeagueService


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
        fantasy_league: FantasyLeagueSettings = Body(...)):
    owner_id = decoded_token.get("user_id")
    return fantasy_league_service.create_fantasy_league(owner_id, fantasy_league)


@router.get(
    path="/leagues/{fantasy_league_id}/settings",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyLeagueSettings
)
def get_fantasy_league_settings(
        fantasy_league_id: str,
        decoded_token: dict = Depends(JWTBearer())):
    owner_id = decoded_token.get("user_id")
    return fantasy_league_service.get_fantasy_league_settings(owner_id, fantasy_league_id)


@router.put(
    path="/leagues/{fantasy_league_id}/settings",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyLeague
)
def update_fantasy_league_settings(
        fantasy_league_id: str,
        fantasy_league_settings: FantasyLeagueSettings = Body(...),
        decoded_token: dict = Depends(JWTBearer())):
    owner_id = decoded_token.get("user_id")
    return fantasy_league_service.update_fantasy_league_settings(
                                    owner_id, fantasy_league_id, fantasy_league_settings)


@router.get(
    path="/leagues/{fantasy_league_id}/scoring",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyLeagueScoringSettings
)
def get_fantasy_league_scoring_settings(
        fantasy_league_id: str,
        decoded_token: dict = Depends(JWTBearer())):
    owner_id = decoded_token.get("user_id")
    return fantasy_league_service.get_scoring_settings(owner_id, fantasy_league_id)


@router.post(
    path="/leagues/{fantasy_league_id}/invite/{username}",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())]
)
def send_invite_user_to_fantasy_league(
        fantasy_league_id: str,
        username: str,
        decoded_token: dict = Depends(JWTBearer())):
    owner_id = decoded_token.get("user_id")
    fantasy_league_service.send_fantasy_league_invite(owner_id, fantasy_league_id, username)


@router.post(
    path="/leagues/{fantasy_league_id}/join",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())]
)
def join_fantasy_league(
        fantasy_league_id: str,
        decoded_token: dict = Depends(JWTBearer())):
    user_id = decoded_token.get("user_id")
    fantasy_league_service.join_fantasy_league(user_id, fantasy_league_id)


@router.post(
    path="/leagues/{fantasy_league_id}/leave",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())]
)
def leave_fantasy_league(
        fantasy_league_id: str,
        decoded_token: dict = Depends(JWTBearer())):
    user_id = decoded_token.get("user_id")
    fantasy_league_service.leave_fantasy_league(user_id, fantasy_league_id)


@router.get(
    path="/leagues/{fantasy_league_id}/draft-order",
    tags=["Fantasy Leagues"],
    response_model=List[FantasyLeagueDraftOrderResponse],
    dependencies=[Depends(JWTBearer())]
)
def get_fantasy_league_draft_order(
        fantasy_league_id: str,
        decoded_token: dict = Depends(JWTBearer())):
    user_id = decoded_token.get("user_id")
    return fantasy_league_service.get_fantasy_league_draft_order(user_id, fantasy_league_id)
