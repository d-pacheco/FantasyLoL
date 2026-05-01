from fastapi.testclient import TestClient

from src.fantasy import app


class TestFantasyAppCors:
    def test_fantasy_api_returns_cors_headers(self):
        client = TestClient(app)
        response = client.get(
            "/api/v1/user/signup",
            headers={"Origin": "http://localhost:3000"},
        )
        assert "access-control-allow-origin" in response.headers
