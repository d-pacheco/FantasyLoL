from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from http import HTTPStatus
from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import riot_fixtures as fixtures

from src.auth import JWTBearer
from src.common.schemas.riot_data_schemas import GameState
from src.riot.exceptions import GameNotFoundException
from src.riot.endpoints import GameEndpoint

GAME_BASE_URL = "/api/v1/game"


class GameEndpointV1Test(TestBase):
    def setUp(self):
        self.mock_service = MagicMock()
        endpoint = GameEndpoint(self.mock_service)
        self.app = FastAPI()
        self.app.include_router(endpoint.router, prefix="/api/v1")
        for route in self.app.routes:
            for dep in getattr(route, "dependencies", []):
                if isinstance(dep.dependency, JWTBearer):
                    self.app.dependency_overrides[dep.dependency] = lambda: {}
        disable_installed_extensions_check()
        add_pagination(self.app)
        self.client = TestClient(self.app)

    def test_get_game_completed_status(self):
        game_fixture = fixtures.game_1_fixture_completed
        expected = game_fixture.model_dump()
        self.mock_service.get_games.return_value = [game_fixture]

        response = self.client.get(f"{GAME_BASE_URL}?state={GameState.COMPLETED.value}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_game_inprogress_status(self):
        game_fixture = fixtures.game_2_fixture_inprogress
        expected = game_fixture.model_dump()
        self.mock_service.get_games.return_value = [game_fixture]

        response = self.client.get(f"{GAME_BASE_URL}?state={GameState.INPROGRESS.value}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_game_unstarted_status(self):
        game_fixture = fixtures.game_3_fixture_unstarted
        expected = game_fixture.model_dump()
        self.mock_service.get_games.return_value = [game_fixture]

        response = self.client.get(f"{GAME_BASE_URL}?state={GameState.UNSTARTED.value}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_game_unneeded_status(self):
        game_fixture = fixtures.game_4_fixture_unneeded
        expected = game_fixture.model_dump()
        self.mock_service.get_games.return_value = [game_fixture]

        response = self.client.get(f"{GAME_BASE_URL}?state={GameState.UNNEEDED.value}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_game_invalid_status(self):
        response = self.client.get(f"{GAME_BASE_URL}?state=invalid")
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)

    def test_get_game_match_id_filter(self):
        game_fixture = fixtures.game_1_fixture_completed
        expected = game_fixture.model_dump()
        self.mock_service.get_games.return_value = [game_fixture]

        response = self.client.get(f"{GAME_BASE_URL}?match_id={game_fixture.match_id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get("items")
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_game_by_id_success(self):
        game_fixture = fixtures.game_1_fixture_completed
        expected = game_fixture.model_dump()
        self.mock_service.get_game_by_id.return_value = game_fixture

        response = self.client.get(f"{GAME_BASE_URL}/{game_fixture.id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected, response.json())

    def test_get_game_by_id_not_found(self):
        self.mock_service.get_game_by_id.side_effect = GameNotFoundException()

        response = self.client.get(f"{GAME_BASE_URL}/777")

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
