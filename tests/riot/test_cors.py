from fastapi.testclient import TestClient

from src.riot import app


class TestRiotAppCors:
    def test_riot_api_returns_cors_headers(self):
        client = TestClient(app)
        response = client.get(
            "/api/v1/league",
            headers={"Origin": "http://localhost:3000"},
        )
        assert "access-control-allow-origin" in response.headers
