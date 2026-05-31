import asyncio

from classy_fastapi import Routable, get, post
from fastapi import Body, Depends

from src.auth import JWTBearer, Permissions
from src.auth.auth_principal import AuthPrincipal
from src.common.schemas.fantasy_schemas import (
    DraftPick,
    DraftState,
    FantasyLeagueID,
    PickMadeEvent,
    DraftCompletedEvent,
    PickRequest,
)
from src.common.schemas.riot_data_schemas import ProfessionalPlayer, ProfessionalTeam
from src.fantasy.service import DraftConnectionManager, DraftService


class DraftEndpoint(Routable):
    def __init__(self, draft_service: DraftService, connection_manager: DraftConnectionManager):
        super().__init__()
        self.__draft_service = draft_service
        self.__connection_manager = connection_manager

    @post(
        path="/leagues/{league_id}/draft/start",
        description="Start the draft for a Fantasy League.",
        tags=["Fantasy Draft"],
    )
    def start_draft(
        self,
        league_id: FantasyLeagueID,
        principal: AuthPrincipal = Depends(JWTBearer([Permissions.FANTASY_WRITE])),
    ) -> None:
        self.__draft_service.start_draft(league_id, principal.user_id)

    @post(
        path="/leagues/{league_id}/draft/pick",
        description="Make a draft pick in a Fantasy League.",
        tags=["Fantasy Draft"],
        response_model=DraftPick,
    )
    def make_pick(
        self,
        league_id: FantasyLeagueID,
        pick_request: PickRequest = Body(...),
        principal: AuthPrincipal = Depends(JWTBearer([Permissions.FANTASY_WRITE])),
    ) -> DraftPick:
        draft_pick = self.__draft_service.make_pick(
            league_id,
            principal.user_id,
            player_id=pick_request.player_id,
            team_id=pick_request.team_id,
        )

        # Determine draft state after pick
        draft_state = self.__draft_service.get_draft_state(league_id, principal.user_id)

        if draft_state.is_complete:
            asyncio.create_task(self.__broadcast_and_close(league_id, draft_pick, draft_state))
        else:
            asyncio.create_task(
                self.__connection_manager.broadcast(
                    league_id,
                    PickMadeEvent(
                        pick=draft_pick,
                        next_turn_user_id=draft_state.current_turn_user_id,
                    ),
                )
            )

        return draft_pick

    async def __broadcast_and_close(self, league_id, draft_pick, draft_state):
        await self.__connection_manager.broadcast(
            league_id,
            PickMadeEvent(pick=draft_pick, next_turn_user_id=None),
        )
        await self.__connection_manager.broadcast(league_id, DraftCompletedEvent())
        await self.__connection_manager.close_room(league_id)

    @get(
        path="/leagues/{league_id}/draft/state",
        description="Get the current draft state for a Fantasy League.",
        tags=["Fantasy Draft"],
        response_model=DraftState,
    )
    def get_draft_state(
        self,
        league_id: FantasyLeagueID,
        principal: AuthPrincipal = Depends(JWTBearer([Permissions.FANTASY_READ])),
    ) -> DraftState:
        return self.__draft_service.get_draft_state(league_id, principal.user_id)

    @get(
        path="/leagues/{league_id}/draft/available-players",
        description="Get available players to draft in a Fantasy League.",
        tags=["Fantasy Draft"],
        response_model=list[ProfessionalPlayer],
    )
    def get_available_players(
        self,
        league_id: FantasyLeagueID,
        principal: AuthPrincipal = Depends(JWTBearer([Permissions.FANTASY_READ])),
    ) -> list[ProfessionalPlayer]:
        return self.__draft_service.get_available_players(league_id, principal.user_id)

    @get(
        path="/leagues/{league_id}/draft/available-teams",
        description="Get available teams to draft in a Fantasy League.",
        tags=["Fantasy Draft"],
        response_model=list[ProfessionalTeam],
    )
    def get_available_teams(
        self,
        league_id: FantasyLeagueID,
        principal: AuthPrincipal = Depends(JWTBearer([Permissions.FANTASY_READ])),
    ) -> list[ProfessionalTeam]:
        return self.__draft_service.get_available_teams(league_id, principal.user_id)
