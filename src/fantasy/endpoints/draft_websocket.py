from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.auth.auth_handler import decode_jwt
from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueMembershipStatus,
    FantasyLeagueStatus,
    UserID,
)
from src.db.database_service import DatabaseService
from src.fantasy.service import DraftConnectionManager


def create_draft_ws_router(
    database_service: DatabaseService,
    connection_manager: DraftConnectionManager,
) -> APIRouter:
    router = APIRouter(tags=["Fantasy Draft"])

    @router.websocket("/leagues/{league_id}/draft/ws")
    async def draft_websocket(
        websocket: WebSocket,
        league_id: FantasyLeagueID,
        token: str | None = None,
    ):
        # Validate token
        if not token:
            await websocket.close(code=4001)
            return

        payload = decode_jwt(token)
        if not payload:
            await websocket.close(code=4001)
            return

        user_id = UserID(payload.get("user_id", ""))

        # Validate league is in DRAFT status
        fantasy_league = database_service.get_fantasy_league_by_id(league_id)
        if fantasy_league is None or fantasy_league.status != FantasyLeagueStatus.DRAFT:
            await websocket.close(code=4002)
            return

        # Validate membership
        membership = database_service.get_user_membership_for_fantasy_league(user_id, league_id)
        if membership is None or membership.status != FantasyLeagueMembershipStatus.ACCEPTED:
            await websocket.close(code=4003)
            return

        # Accept and register connection
        await websocket.accept()
        connection_manager.connect(league_id, websocket)

        try:
            while True:
                # Keep connection alive — WebSocket is read-only push
                await websocket.receive_text()
        except WebSocketDisconnect:
            connection_manager.disconnect(league_id, websocket)

    return router
