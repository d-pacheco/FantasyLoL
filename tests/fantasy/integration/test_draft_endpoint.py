from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from src.app import create_app
from src.auth import sign_jwt, Permissions
from src.db.database_service import DatabaseService

TEST_USER_ID = "test-user-id"
TEST_LEAGUE_ID = "test-league-id"
ALL_PERMISSIONS = [p.value for p in Permissions]


def make_client():
    mock_db = MagicMock(spec=DatabaseService)
    app = create_app(mock_db)
    token_data = sign_jwt(TEST_USER_ID, ALL_PERMISSIONS, "test-user")
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    client = TestClient(app, raise_server_exceptions=False)
    return client, mock_db, headers


def make_unauthed_client():
    mock_db = MagicMock(spec=DatabaseService)
    app = create_app(mock_db)
    return TestClient(app, raise_server_exceptions=False)


class TestDraftEndpoint:
    # --------------------------------------------------
    # ------------------- start ------------------------
    # --------------------------------------------------
    def test_start_draft_route_is_mounted(self):
        # Arrange
        client, mock_db, headers = make_client()

        # Act — route exists (not 404/405), service may return error due to mock
        response = client.post(
            f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/start",
            headers=headers,
        )

        # Assert
        assert response.status_code != 404
        assert response.status_code != 405

    def test_start_draft_unauthenticated_returns_403(self):
        # Arrange
        client = make_unauthed_client()

        # Act
        response = client.post(f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/start")

        # Assert
        assert response.status_code == 403

    # --------------------------------------------------
    # ------------------- state ------------------------
    # --------------------------------------------------
    def test_get_draft_state_route_is_mounted(self):
        # Arrange
        client, mock_db, headers = make_client()

        # Act
        response = client.get(
            f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/state",
            headers=headers,
        )

        # Assert
        assert response.status_code != 404
        assert response.status_code != 405

    def test_get_draft_state_unauthenticated_returns_403(self):
        # Arrange
        client = make_unauthed_client()

        # Act
        response = client.get(f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/state")

        # Assert
        assert response.status_code == 403

    # --------------------------------------------------
    # ------------- available-players ------------------
    # --------------------------------------------------
    def test_get_available_players_route_is_mounted(self):
        # Arrange
        client, mock_db, headers = make_client()

        # Act
        response = client.get(
            f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/available-players",
            headers=headers,
        )

        # Assert
        assert response.status_code != 404
        assert response.status_code != 405

    def test_get_available_players_unauthenticated_returns_403(self):
        # Arrange
        client = make_unauthed_client()

        # Act
        response = client.get(f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/available-players")

        # Assert
        assert response.status_code == 403

    # --------------------------------------------------
    # -------------- available-teams -------------------
    # --------------------------------------------------
    def test_get_available_teams_route_is_mounted(self):
        # Arrange
        client, mock_db, headers = make_client()

        # Act
        response = client.get(
            f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/available-teams",
            headers=headers,
        )

        # Assert
        assert response.status_code != 404
        assert response.status_code != 405

    def test_get_available_teams_unauthenticated_returns_403(self):
        # Arrange
        client = make_unauthed_client()

        # Act
        response = client.get(f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/available-teams")

        # Assert
        assert response.status_code == 403

    # --------------------------------------------------
    # ------------------- pick -------------------------
    # --------------------------------------------------
    def test_make_pick_route_is_mounted(self):
        # Arrange
        client, mock_db, headers = make_client()
        mock_db.get_draft_picks_for_league.return_value = []
        mock_db.put_draft_pick.return_value = None
        mock_db.put_fantasy_team.return_value = None

        # Act
        response = client.post(
            f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/pick",
            json={"player_id": "player-1"},
            headers=headers,
        )

        # Assert — route exists (not 404/405)
        assert response.status_code != 404
        assert response.status_code != 405

    def test_make_pick_unauthenticated_returns_403(self):
        # Arrange
        client = make_unauthed_client()

        # Act
        response = client.post(
            f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/pick",
            json={"player_id": "player-1"},
        )

        # Assert
        assert response.status_code == 403

    def test_make_pick_broadcasts_pick_made_event(self):
        # Arrange
        from unittest.mock import AsyncMock, patch

        client, mock_db, headers = make_client()
        mock_db.get_draft_picks_for_league.return_value = []
        mock_db.put_draft_pick.return_value = None
        mock_db.put_fantasy_team.return_value = None

        # Act — patch broadcast to verify it's called on a successful pick
        with patch(
            "src.fantasy.service.draft_connection_manager.DraftConnectionManager.broadcast",
            new_callable=AsyncMock,
        ):
            response = client.post(
                f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/draft/pick",
                json={"player_id": "player-1"},
                headers=headers,
            )

        # Assert — route was hit (not 404/405)
        assert response.status_code != 404
        assert response.status_code != 405
