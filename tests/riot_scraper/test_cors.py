from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from src.riot_scraper.app import configure_api_endpoints
from src.riot_scraper.job_runner_endpoint import JobRunnerEndpoint


class TestScraperAppCors:
    def test_scraper_api_returns_cors_headers(self):
        mock_scheduler = MagicMock()
        endpoint = JobRunnerEndpoint(mock_scheduler)
        app = configure_api_endpoints(endpoint)
        client = TestClient(app)

        response = client.post(
            "/api/v1/fetch-leagues",
            headers={"Origin": "http://localhost:3000"},
        )
        assert "access-control-allow-origin" in response.headers
