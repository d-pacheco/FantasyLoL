from fastapi import APIRouter, Body, Depends
from typing import List

from src.auth import JWTBearer

from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueID,
    FantasyLeagueSettings,
    FantasyLeagueScoringSettings,
    UsersFantasyLeagues,
    FantasyLeagueDraftOrderResponse,
    UserID
)

from src.fantasy.service import FantasyLeagueService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
fantasy_league_service = FantasyLeagueService()


@router.get(
    path="/leagues",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())],
    response_model=UsersFantasyLeagues
)
def get_my_fantasy_leagues(
        decoded_token: dict = Depends(JWTBearer())) -> UsersFantasyLeagues:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return fantasy_league_service.get_users_pending_and_accepted_fantasy_leagues(user_id)


@router.post(
    path="/leagues",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyLeague
)
def create_fantasy_league(
        decoded_token: dict = Depends(JWTBearer()),
        fantasy_league: FantasyLeagueSettings = Body(...)) -> FantasyLeague:
    owner_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return fantasy_league_service.create_fantasy_league(owner_id, fantasy_league)


@router.get(
    path="/leagues/{fantasy_league_id}/settings",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyLeagueSettings
)
def get_fantasy_league_settings(
        fantasy_league_id: FantasyLeagueID,
        decoded_token: dict = Depends(JWTBearer())) -> FantasyLeagueSettings:
    owner_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return fantasy_league_service.get_fantasy_league_settings(owner_id, fantasy_league_id)


@router.put(
    path="/leagues/{fantasy_league_id}/settings",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyLeagueSettings
)
def update_fantasy_league_settings(
        fantasy_league_id: FantasyLeagueID,
        fantasy_league_settings: FantasyLeagueSettings = Body(...),
        decoded_token: dict = Depends(JWTBearer())) -> FantasyLeagueSettings:
    owner_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return fantasy_league_service.update_fantasy_league_settings(
        owner_id, fantasy_league_id, fantasy_league_settings)


@router.get(
    path="/leagues/{fantasy_league_id}/scoring",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyLeagueScoringSettings
)
def get_fantasy_league_scoring_settings(
        fantasy_league_id: FantasyLeagueID,
        decoded_token: dict = Depends(JWTBearer())) -> FantasyLeagueScoringSettings:
    owner_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return fantasy_league_service.get_scoring_settings(owner_id, fantasy_league_id)


@router.put(
    path="/leagues/{fantasy_league_id}/scoring",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())],
    response_model=FantasyLeagueScoringSettings
)
def update_fantasy_league_scoring_settings(
        fantasy_league_id: FantasyLeagueID,
        scoring_settings: FantasyLeagueScoringSettings = Body(...),
        decoded_token: dict = Depends(JWTBearer())) -> FantasyLeagueScoringSettings:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return fantasy_league_service.update_scoring_settings(
        fantasy_league_id, user_id, scoring_settings
    )


@router.post(
    path="/leagues/{fantasy_league_id}/invite/{username}",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())]
)
def send_invite_user_to_fantasy_league(
        fantasy_league_id: FantasyLeagueID,
        username: str,
        decoded_token: dict = Depends(JWTBearer())) -> None:
    owner_id = UserID(decoded_token.get("user_id"))  # type: ignore
    fantasy_league_service.send_fantasy_league_invite(owner_id, fantasy_league_id, username)


@router.post(
    path="/leagues/{fantasy_league_id}/join",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())]
)
def join_fantasy_league(
        fantasy_league_id: FantasyLeagueID,
        decoded_token: dict = Depends(JWTBearer())) -> None:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    fantasy_league_service.join_fantasy_league(user_id, fantasy_league_id)


@router.post(
    path="/leagues/{fantasy_league_id}/leave",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())]
)
def leave_fantasy_league(
        fantasy_league_id: FantasyLeagueID,
        decoded_token: dict = Depends(JWTBearer())) -> None:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    fantasy_league_service.leave_fantasy_league(user_id, fantasy_league_id)


@router.post(
    path="/leagues/{fantasy_league_id}/revoke/{user_id_to_revoke}",
    tags=["Fantasy Leagues"],
    status_code=204,
    dependencies=[Depends(JWTBearer())]
)
def revoke_from_fantasy_league(
        fantasy_league_id: FantasyLeagueID,
        user_id_to_revoke: UserID,
        decoded_token: dict = Depends(JWTBearer())) -> None:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    fantasy_league_service.revoke_from_fantasy_league(
        fantasy_league_id, user_id, user_id_to_revoke
    )


@router.get(
    path="/leagues/{fantasy_league_id}/draft-order",
    tags=["Fantasy Leagues"],
    response_model=List[FantasyLeagueDraftOrderResponse],
    dependencies=[Depends(JWTBearer())]
)
def get_fantasy_league_draft_order(
        fantasy_league_id: FantasyLeagueID,
        decoded_token: dict = Depends(JWTBearer())) -> List[FantasyLeagueDraftOrderResponse]:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    return fantasy_league_service.get_fantasy_league_draft_order(user_id, fantasy_league_id)


@router.put(
    path="/leagues/{fantasy_league_id}/draft-order",
    tags=["Fantasy Leagues"],
    dependencies=[Depends(JWTBearer())]
)
def update_fantasy_league_draft_order(
        fantasy_league_id: FantasyLeagueID,
        decoded_token: dict = Depends(JWTBearer()),
        updated_draft_order: List[FantasyLeagueDraftOrderResponse] = Body(...)) -> None:
    user_id = UserID(decoded_token.get("user_id"))  # type: ignore
    fantasy_league_service.update_fantasy_league_draft_order(
        user_id, fantasy_league_id, updated_draft_order
    )
