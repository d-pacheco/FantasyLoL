from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from http import HTTPStatus
from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import riot_fixtures as fixtures

from src.auth import JWTBearer
from src.riot.exceptions import ProfessionalTeamNotFoundException
from src.riot.endpoints import ProfessionalTeamEndpoint

TEAM_BASE_URL = "/api/v1/professional-team"


class ProfessionalTeamEndpointV1Test(TestBase):
    def setUp(self):
        self.mock_service = MagicMock()
        endpoint = ProfessionalTeamEndpoint(self.mock_service)
        self.app = FastAPI()
        self.app.include_router(endpoint.router, prefix="/api/v1")
        for route in self.app.routes:
            for dep in getattr(route, 'dependencies', []):
                if isinstance(dep.dependency, JWTBearer):
                    self.app.dependency_overrides[dep.dependency] = lambda: {}
        disable_installed_extensions_check()
        add_pagination(self.app)
        self.client = TestClient(self.app)

    def test_get_teams_slug_query(self):
        team_fixture = fixtures.team_1_fixture
        expected = team_fixture.model_dump()
        self.mock_service.get_teams.return_value = [team_fixture]

        response = self.client.get(f"{TEAM_BASE_URL}?slug={team_fixture.slug}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_teams_name_query(self):
        team_fixture = fixtures.team_1_fixture
        expected = team_fixture.model_dump()
        self.mock_service.get_teams.return_value = [team_fixture]

        response = self.client.get(f"{TEAM_BASE_URL}?name={team_fixture.name}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_teams_code_query(self):
        team_fixture = fixtures.team_1_fixture
        expected = team_fixture.model_dump()
        self.mock_service.get_teams.return_value = [team_fixture]

        response = self.client.get(f"{TEAM_BASE_URL}?code={team_fixture.code}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_teams_status_query(self):
        team_fixture = fixtures.team_1_fixture
        expected = team_fixture.model_dump()
        self.mock_service.get_teams.return_value = [team_fixture]

        response = self.client.get(f"{TEAM_BASE_URL}?status={team_fixture.status}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_teams_league_query(self):
        team_fixture = fixtures.team_1_fixture
        expected = team_fixture.model_dump()
        self.mock_service.get_teams.return_value = [team_fixture]

        response = self.client.get(f"{TEAM_BASE_URL}?league={team_fixture.home_league}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_teams_search_all(self):
        team_fixture = fixtures.team_1_fixture
        expected = team_fixture.model_dump()
        self.mock_service.get_teams.return_value = [team_fixture]

        response = self.client.get(TEAM_BASE_URL)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_team_by_id_success(self):
        team_fixture = fixtures.team_1_fixture
        expected = team_fixture.model_dump()
        self.mock_service.get_team_by_id.return_value = team_fixture

        response = self.client.get(f"{TEAM_BASE_URL}/{team_fixture.id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected, response.json())

    def test_get_team_by_id_not_found(self):
        team_fixture = fixtures.team_1_fixture
        self.mock_service.get_team_by_id.side_effect = ProfessionalTeamNotFoundException()

        response = self.client.get(f"{TEAM_BASE_URL}/{team_fixture.id}")

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
