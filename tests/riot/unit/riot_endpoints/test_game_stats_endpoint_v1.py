from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from http import HTTPStatus
from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import riot_fixtures as fixtures

from src.auth import JWTBearer
from src.riot.endpoints import GameStatsEndpoint

GAME_STATS_BASE_URL = "/api/v1/stats"


class GameStatsEndpointV1Test(TestBase):
    def setUp(self):
        self.mock_service = MagicMock()
        endpoint = GameStatsEndpoint(self.mock_service)
        self.app = FastAPI()
        self.app.include_router(endpoint.router, prefix="/api/v1")
        for route in self.app.routes:
            for dep in getattr(route, "dependencies", []):
                if isinstance(dep.dependency, JWTBearer):
                    self.app.dependency_overrides[dep.dependency] = lambda: {}
        disable_installed_extensions_check()
        add_pagination(self.app)
        self.client = TestClient(self.app)

    def test_get_player_stats_no_filters_existing_data(self):
        fixture = fixtures.player_1_game_data_fixture
        expected = fixture.model_dump()
        self.mock_service.get_player_stats.return_value = [fixture]

        response = self.client.get(f"{GAME_STATS_BASE_URL}/player")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_player_stats_no_filters_no_data(self):
        self.mock_service.get_player_stats.return_value = []

        response = self.client.get(f"{GAME_STATS_BASE_URL}/player")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(0, len(items))

    def test_get_player_stats_filter_by_game_id_existing_data(self):
        fixture = fixtures.player_1_game_data_fixture
        expected = fixture.model_dump()
        self.mock_service.get_player_stats.return_value = [fixture]

        response = self.client.get(f"{GAME_STATS_BASE_URL}/player?game_id={fixture.game_id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_player_stats_filter_by_game_id_no_data(self):
        fixture = fixtures.player_1_game_data_fixture
        self.mock_service.get_player_stats.return_value = []

        response = self.client.get(f"{GAME_STATS_BASE_URL}/player?game_id={fixture.game_id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(0, len(items))

    def test_get_player_stats_filter_by_player_id_existing_data(self):
        fixture = fixtures.player_1_game_data_fixture
        expected = fixture.model_dump()
        self.mock_service.get_player_stats.return_value = [fixture]

        response = self.client.get(f"{GAME_STATS_BASE_URL}/player?player_id={fixture.player_id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_player_stats_filter_by_player_id_no_data(self):
        fixture = fixtures.player_1_game_data_fixture
        self.mock_service.get_player_stats.return_value = []

        response = self.client.get(f"{GAME_STATS_BASE_URL}/player?player_id={fixture.player_id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(0, len(items))
