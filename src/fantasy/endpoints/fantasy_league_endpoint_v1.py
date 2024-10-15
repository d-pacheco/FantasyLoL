from classy_fastapi import Routable, get, post, put
from fastapi import Body, Depends
from typing import List

from src.auth import JWTBearer, Permissions
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


class FantasyLeagueEndpoint(Routable):
    def __init__(self, fantasy_league_service: FantasyLeagueService):
        super().__init__()
        self.__fantasy_league_service = fantasy_league_service

    @get(
        path="/leagues",
        tags=["Fantasy Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_READ]))],
        response_model=UsersFantasyLeagues
    )
    def get_my_fantasy_leagues(
            self,
            decoded_token: dict = Depends(JWTBearer())
    ) -> UsersFantasyLeagues:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_league_service.get_users_pending_and_accepted_fantasy_leagues(user_id)

    @post(
        path="/leagues",
        tags=["Fantasy Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))],
        response_model=FantasyLeague
    )
    def create_fantasy_league(
            self,
            decoded_token: dict = Depends(JWTBearer()),
            fantasy_league: FantasyLeagueSettings = Body(...)
    ) -> FantasyLeague:
        owner_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_league_service.create_fantasy_league(owner_id, fantasy_league)

    @get(
        path="/leagues/{fantasy_league_id}/settings",
        tags=["Fantasy Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_READ]))],
        response_model=FantasyLeagueSettings
    )
    def get_fantasy_league_settings(
            self,
            fantasy_league_id: FantasyLeagueID,
            decoded_token: dict = Depends(JWTBearer())
    ) -> FantasyLeagueSettings:
        owner_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_league_service.get_fantasy_league_settings(
            owner_id,
            fantasy_league_id
        )

    @put(
        path="/leagues/{fantasy_league_id}/settings",
        tags=["Fantasy Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))],
        response_model=FantasyLeagueSettings
    )
    def update_fantasy_league_settings(
            self,
            fantasy_league_id: FantasyLeagueID,
            fantasy_league_settings: FantasyLeagueSettings = Body(...),
            decoded_token: dict = Depends(JWTBearer())
    ) -> FantasyLeagueSettings:
        owner_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_league_service.update_fantasy_league_settings(
            owner_id, fantasy_league_id, fantasy_league_settings)

    @get(
        path="/leagues/{fantasy_league_id}/scoring",
        tags=["Fantasy Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_READ]))],
        response_model=FantasyLeagueScoringSettings
    )
    def get_fantasy_league_scoring_settings(
            self,
            fantasy_league_id: FantasyLeagueID,
            decoded_token: dict = Depends(JWTBearer())
    ) -> FantasyLeagueScoringSettings:
        owner_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_league_service.get_scoring_settings(owner_id, fantasy_league_id)

    @put(
        path="/leagues/{fantasy_league_id}/scoring",
        tags=["Fantasy Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))],
        response_model=FantasyLeagueScoringSettings
    )
    def update_fantasy_league_scoring_settings(
            self,
            fantasy_league_id: FantasyLeagueID,
            scoring_settings: FantasyLeagueScoringSettings = Body(...),
            decoded_token: dict = Depends(JWTBearer())
    ) -> FantasyLeagueScoringSettings:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_league_service.update_scoring_settings(
            fantasy_league_id, user_id, scoring_settings
        )

    @post(
        path="/leagues/{fantasy_league_id}/invite/{username}",
        tags=["Fantasy Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))]
    )
    def send_invite_user_to_fantasy_league(
            self,
            fantasy_league_id: FantasyLeagueID,
            username: str,
            decoded_token: dict = Depends(JWTBearer())
    ) -> None:
        owner_id = UserID(decoded_token.get("user_id"))  # type: ignore
        self.__fantasy_league_service.send_fantasy_league_invite(
            owner_id,
            fantasy_league_id,
            username
        )

    @post(
        path="/leagues/{fantasy_league_id}/join",
        tags=["Fantasy Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))]
    )
    def join_fantasy_league(
            self,
            fantasy_league_id: FantasyLeagueID,
            decoded_token: dict = Depends(JWTBearer())
    ) -> None:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        self.__fantasy_league_service.join_fantasy_league(user_id, fantasy_league_id)

    @post(
        path="/leagues/{fantasy_league_id}/leave",
        tags=["Fantasy Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))]
    )
    def leave_fantasy_league(
            self,
            fantasy_league_id: FantasyLeagueID,
            decoded_token: dict = Depends(JWTBearer())
    ) -> None:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        self.__fantasy_league_service.leave_fantasy_league(user_id, fantasy_league_id)

    @post(
        path="/leagues/{fantasy_league_id}/revoke/{user_id_to_revoke}",
        tags=["Fantasy Leagues"],
        status_code=204,
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))]
    )
    def revoke_from_fantasy_league(
            self,
            fantasy_league_id: FantasyLeagueID,
            user_id_to_revoke: UserID,
            decoded_token: dict = Depends(JWTBearer())
    ) -> None:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        self.__fantasy_league_service.revoke_from_fantasy_league(
            fantasy_league_id,
            user_id,
            user_id_to_revoke
        )

    @get(
        path="/leagues/{fantasy_league_id}/draft-order",
        tags=["Fantasy Leagues"],
        response_model=List[FantasyLeagueDraftOrderResponse],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_READ]))]
    )
    def get_fantasy_league_draft_order(
            self,
            fantasy_league_id: FantasyLeagueID,
            decoded_token: dict = Depends(JWTBearer())
    ) -> List[FantasyLeagueDraftOrderResponse]:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_league_service.get_fantasy_league_draft_order(
            user_id,
            fantasy_league_id
        )

    @put(
        path="/leagues/{fantasy_league_id}/draft-order",
        tags=["Fantasy Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))]
    )
    def update_fantasy_league_draft_order(
            self,
            fantasy_league_id: FantasyLeagueID,
            decoded_token: dict = Depends(JWTBearer()),
            updated_draft_order: List[FantasyLeagueDraftOrderResponse] = Body(...)
    ) -> None:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        self.__fantasy_league_service.update_fantasy_league_draft_order(
            user_id,
            fantasy_league_id,
            updated_draft_order
        )
