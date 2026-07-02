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


class TestLeaderboardEndpoint:
    def test_leaderboard_route_is_mounted(self):
        """The leaderboard endpoint should exist and not return 404."""
        client, mock_db, headers = make_client()

        response = client.get(
            f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/leaderboard",
            headers=headers,
        )

        # Should not be 404 (route exists). May be 500 due to mock, but not 404/405.
        assert response.status_code != 404
        assert response.status_code != 405

    def test_leaderboard_requires_auth(self):
        """Unauthenticated requests should be rejected."""
        mock_db = MagicMock(spec=DatabaseService)
        app = create_app(mock_db)
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get(
            f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/leaderboard",
        )

        assert response.status_code == 403


class TestWeekScoresEndpoint:
    def test_week_scores_route_is_mounted(self):
        """The week scores endpoint should exist and not return 404."""
        client, mock_db, headers = make_client()

        response = client.get(
            f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/scores?week=1",
            headers=headers,
        )

        assert response.status_code != 404
        assert response.status_code != 405

    def test_week_scores_requires_auth(self):
        """Unauthenticated requests should be rejected."""
        mock_db = MagicMock(spec=DatabaseService)
        app = create_app(mock_db)
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get(
            f"/api/v1/fantasy/leagues/{TEST_LEAGUE_ID}/scores?week=1",
        )

        assert response.status_code == 403
