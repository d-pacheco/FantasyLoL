from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from src.app import create_app
from src.auth import JWTBearer, sign_jwt, Permissions
from src.auth.auth_principal import AuthPrincipal
from src.db.database_service import DatabaseService

TEST_USER_ID = "test-user-id"
ALL_PERMISSIONS = [p.value for p in Permissions]


def make_client():
    mock_db = MagicMock(spec=DatabaseService)
    app = create_app(mock_db)
    # Override all JWTBearer dependencies to return a test principal
    test_principal = AuthPrincipal(user_id=TEST_USER_ID, permissions=ALL_PERMISSIONS)
    for route in app.routes:
        for dep in getattr(route, "dependencies", []):
            if isinstance(dep.dependency, JWTBearer):
                app.dependency_overrides[dep.dependency] = lambda: test_principal
    # Also override for parameter-level Depends
    token_data = sign_jwt(TEST_USER_ID, ALL_PERMISSIONS, "test-user")
    auth_header = {"Authorization": f"Bearer {token_data['access_token']}"}
    return TestClient(app), mock_db, auth_header


class TestUnifiedAppRiotRoutes:
    def test_riot_league_endpoint_is_reachable(self):
        client, mock_db, headers = make_client()
        mock_db.get_leagues.return_value = []
        response = client.get("/api/v1/riot/league", headers=headers)
        assert response.status_code == 200

    def test_riot_route_returns_cors_headers(self):
        client, mock_db, headers = make_client()
        mock_db.get_leagues.return_value = []
        response = client.get(
            "/api/v1/riot/league",
            headers={**headers, "Origin": "http://localhost:3000"},
        )
        assert "access-control-allow-origin" in response.headers


class TestUnifiedAppFantasyRoutes:
    def test_fantasy_leagues_endpoint_is_reachable(self):
        client, mock_db, headers = make_client()
        mock_db.get_users_fantasy_leagues_with_membership_status.return_value = []
        response = client.get("/api/v1/fantasy/leagues", headers=headers)
        assert response.status_code == 200


class TestUnifiedAppUserRoutes:
    def test_user_signup_endpoint_is_reachable(self):
        client, mock_db, headers = make_client()
        mock_db.get_user_by_username.return_value = None
        mock_db.get_user_by_email.return_value = None
        mock_db.get_user_by_id.return_value = None
        mock_db.create_user.return_value = None
        response = client.post(
            "/api/v1/user/signup",
            json={"username": "testuser", "email": "test@example.com", "password": "pass1234"},
        )
        # Endpoint is reachable (not 404/405). May return 200 or 400 depending
        # on email verification config, but proves the route is mounted.
        assert response.status_code != 404
        assert response.status_code != 405


class TestOldRoutesAreGone:
    def test_old_riot_league_path_returns_404(self):
        client, mock_db, headers = make_client()
        response = client.get("/api/v1/league", headers=headers)
        assert response.status_code == 404

    def test_old_fantasy_leagues_path_returns_404(self):
        client, mock_db, headers = make_client()
        response = client.get("/api/v1/leagues", headers=headers)
        assert response.status_code == 404
