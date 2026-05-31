from classy_fastapi import Routable, get, post
from fastapi import Depends

from src.auth import JWTBearer, Permissions
from src.auth.auth_principal import AuthPrincipal
from src.common.schemas.fantasy_schemas import (
    DraftState,
    FantasyLeagueID,
)
from src.common.schemas.riot_data_schemas import ProfessionalPlayer, ProfessionalTeam
from src.fantasy.service import DraftService


class DraftEndpoint(Routable):
    def __init__(self, draft_service: DraftService):
        super().__init__()
        self.__draft_service = draft_service

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
