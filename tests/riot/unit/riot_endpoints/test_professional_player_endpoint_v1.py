from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from http import HTTPStatus
from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import riot_fixtures as fixtures

from src.auth import JWTBearer
from src.common.exceptions import ProfessionalPlayerNotFoundException
from src.riot.endpoints import ProfessionalPlayerEndpoint

PLAYER_BASE_URL = "/api/v1/professional-player"


class ProfessionalPlayerEndpointV1Test(TestBase):
    def setUp(self):
        self.mock_service = MagicMock()
        endpoint = ProfessionalPlayerEndpoint(self.mock_service)
        self.app = FastAPI()
        self.app.include_router(endpoint.router, prefix="/api/v1")
        for route in self.app.routes:
            for dep in getattr(route, 'dependencies', []):
                if isinstance(dep.dependency, JWTBearer):
                    self.app.dependency_overrides[dep.dependency] = lambda: {}
        disable_installed_extensions_check()
        add_pagination(self.app)
        self.client = TestClient(self.app)

    def test_get_players_summoner_name_query(self):
        player_fixture = fixtures.player_1_fixture
        expected = player_fixture.model_dump()
        self.mock_service.get_players.return_value = [player_fixture]

        response = self.client.get(
            f"{PLAYER_BASE_URL}?summoner_name={player_fixture.summoner_name}"
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_players_role_query(self):
        player_fixture = fixtures.player_1_fixture
        expected = player_fixture.model_dump()
        self.mock_service.get_players.return_value = [player_fixture]

        response = self.client.get(f"{PLAYER_BASE_URL}?role={player_fixture.role.value}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_players_team_id_query(self):
        player_fixture = fixtures.player_1_fixture
        expected = player_fixture.model_dump()
        self.mock_service.get_players.return_value = [player_fixture]

        response = self.client.get(f"{PLAYER_BASE_URL}?team_id={player_fixture.team_id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_players_search_all(self):
        player_fixture = fixtures.player_1_fixture
        expected = player_fixture.model_dump()
        self.mock_service.get_players.return_value = [player_fixture]

        response = self.client.get(PLAYER_BASE_URL)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_player_by_id_success(self):
        player_fixture = fixtures.player_1_fixture
        expected = player_fixture.model_dump()
        self.mock_service.get_player_by_id.return_value = player_fixture

        response = self.client.get(f"{PLAYER_BASE_URL}/{player_fixture.id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected, response.json())

    def test_get_player_by_id_not_found(self):
        player_fixture = fixtures.player_1_fixture
        self.mock_service.get_player_by_id.side_effect = \
            ProfessionalPlayerNotFoundException()

        response = self.client.get(f"{PLAYER_BASE_URL}/{player_fixture.id}")

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
