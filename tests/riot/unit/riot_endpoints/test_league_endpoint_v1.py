from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from http import HTTPStatus
from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import riot_fixtures as fixtures

from src.auth import JWTBearer
from src.common.exceptions import LeagueNotFoundException
from src.common.schemas.search_parameters import LeagueSearchParameters
from src.riot.endpoints import LeagueEndpoint

LEAGUE_BASE_URL = "/api/v1/league"


class LeagueEndpointV1Test(TestBase):
    def setUp(self):
        self.mock_service = MagicMock()
        endpoint = LeagueEndpoint(self.mock_service)
        self.app = FastAPI()
        self.app.include_router(endpoint.router, prefix="/api/v1")
        # Override every JWTBearer instance used in route dependencies
        for route in self.app.routes:
            for dep in getattr(route, 'dependencies', []):
                if isinstance(dep.dependency, JWTBearer):
                    self.app.dependency_overrides[dep.dependency] = lambda: {}
        disable_installed_extensions_check()
        add_pagination(self.app)
        self.client = TestClient(self.app)

    def test_get_leagues_endpoint_search_all(self):
        league_fixture = fixtures.league_1_fixture
        expected = league_fixture.model_dump()
        self.mock_service.get_leagues.return_value = [league_fixture]

        response = self.client.get(LEAGUE_BASE_URL)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])
        self.mock_service.get_leagues.assert_called_once_with(LeagueSearchParameters())

    def test_get_leagues_endpoint_name_filter(self):
        league_fixture = fixtures.league_1_fixture
        expected = league_fixture.model_dump()
        self.mock_service.get_leagues.return_value = [league_fixture]

        response = self.client.get(f"{LEAGUE_BASE_URL}?name={league_fixture.name}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])
        self.mock_service.get_leagues.assert_called_once_with(
            LeagueSearchParameters(name=league_fixture.name)
        )

    def test_get_leagues_endpoint_region_filter(self):
        league_fixture = fixtures.league_1_fixture
        expected = league_fixture.model_dump()
        self.mock_service.get_leagues.return_value = [league_fixture]

        response = self.client.get(f"{LEAGUE_BASE_URL}?region={league_fixture.region}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])
        self.mock_service.get_leagues.assert_called_once_with(
            LeagueSearchParameters(region=league_fixture.region)
        )

    def test_get_leagues_endpoint_fantasy_available_filter(self):
        league_fixture = fixtures.league_1_fixture
        expected = league_fixture.model_dump()
        self.mock_service.get_leagues.return_value = [league_fixture]

        response = self.client.get(
            f"{LEAGUE_BASE_URL}?fantasy_available={league_fixture.fantasy_available}"
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])
        self.mock_service.get_leagues.assert_called_once_with(
            LeagueSearchParameters(fantasy_available=league_fixture.fantasy_available)
        )

    def test_get_league_by_id_success(self):
        league_fixture = fixtures.league_1_fixture
        expected = league_fixture.model_dump()
        self.mock_service.get_league_by_id.return_value = league_fixture

        response = self.client.get(f"{LEAGUE_BASE_URL}/{league_fixture.id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected, response.json())
        self.mock_service.get_league_by_id.assert_called_once_with(league_fixture.id)

    def test_get_league_by_id_not_found(self):
        league_fixture = fixtures.league_1_fixture
        self.mock_service.get_league_by_id.side_effect = \
            LeagueNotFoundException(league_fixture.id)

        response = self.client.get(f"{LEAGUE_BASE_URL}/{league_fixture.id}")

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        self.mock_service.get_league_by_id.assert_called_once_with(league_fixture.id)
