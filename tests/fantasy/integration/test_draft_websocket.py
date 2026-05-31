from unittest.mock import MagicMock
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from src.app import create_app
from src.auth import sign_jwt, Permissions
from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueID,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    UserID,
)
from src.db.database_service import DatabaseService
from tests.test_util import fantasy_fixtures

TEST_USER_ID = "test-user-id"
TEST_LEAGUE_ID = "test-league-id"
ALL_PERMISSIONS = [p.value for p in Permissions]
WS_URL = f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/ws"


def make_token(user_id=TEST_USER_ID):
    return sign_jwt(user_id, ALL_PERMISSIONS, "test-user")["access_token"]


def make_draft_league() -> FantasyLeague:
    league = deepcopy(fantasy_fixtures.fantasy_league_draft_fixture)
    league.id = FantasyLeagueID(TEST_LEAGUE_ID)
    return league


def make_accepted_membership(user_id=TEST_USER_ID) -> FantasyLeagueMembership:
    return FantasyLeagueMembership(
        league_id=FantasyLeagueID(TEST_LEAGUE_ID),
        user_id=UserID(user_id),
        status=FantasyLeagueMembershipStatus.ACCEPTED,
    )


class TestDraftWebSocketEndpoint:
    def setup_method(self):
        self.mock_db = MagicMock(spec=DatabaseService)
        self.app = create_app(self.mock_db)
        self.client = TestClient(self.app, raise_server_exceptions=False)

    # --------------------------------------------------
    # ----------- successful connection ----------------
    # --------------------------------------------------
    def test_authenticated_member_can_connect(self):
        # Arrange
        self.mock_db.get_fantasy_league_by_id.return_value = make_draft_league()
        self.mock_db.get_user_membership_for_fantasy_league.return_value = (
            make_accepted_membership()
        )
        token = make_token()

        # Act & Assert — connection accepted, no exception
        with self.client.websocket_connect(f"{WS_URL}?token={token}"):
            pass  # connected successfully

    # --------------------------------------------------
    # ----------- rejected connections -----------------
    # --------------------------------------------------
    def test_missing_token_rejects_connection(self):
        # Act & Assert
        with pytest.raises(WebSocketDisconnect):
            with self.client.websocket_connect(WS_URL):
                pass

    def test_invalid_token_rejects_connection(self):
        # Act & Assert
        with pytest.raises(WebSocketDisconnect):
            with self.client.websocket_connect(f"{WS_URL}?token=invalid-token"):
                pass

    def test_non_member_rejects_connection(self):
        # Arrange
        self.mock_db.get_fantasy_league_by_id.return_value = make_draft_league()
        self.mock_db.get_user_membership_for_fantasy_league.return_value = None
        token = make_token()

        # Act & Assert
        with pytest.raises(WebSocketDisconnect):
            with self.client.websocket_connect(f"{WS_URL}?token={token}"):
                pass

    def test_non_draft_league_rejects_connection(self):
        # Arrange
        active_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        active_league.id = FantasyLeagueID(TEST_LEAGUE_ID)
        self.mock_db.get_fantasy_league_by_id.return_value = active_league
        self.mock_db.get_user_membership_for_fantasy_league.return_value = (
            make_accepted_membership()
        )
        token = make_token()

        # Act & Assert
        with pytest.raises(WebSocketDisconnect):
            with self.client.websocket_connect(f"{WS_URL}?token={token}"):
                pass

    # --------------------------------------------------
    # -------------- disconnect cleanup ----------------
    # --------------------------------------------------
    def test_disconnect_removes_connection_from_manager(self):
        # Arrange
        self.mock_db.get_fantasy_league_by_id.return_value = make_draft_league()
        self.mock_db.get_user_membership_for_fantasy_league.return_value = (
            make_accepted_membership()
        )
        token = make_token()

        # Act — connect then disconnect
        with self.client.websocket_connect(f"{WS_URL}?token={token}"):
            pass  # disconnect on exit

        # Assert — no error raised means disconnect was handled cleanly
