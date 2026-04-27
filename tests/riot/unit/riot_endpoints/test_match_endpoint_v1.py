from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from http import HTTPStatus
from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import riot_fixtures as fixtures

from src.auth import JWTBearer
from src.riot.exceptions import MatchNotFoundException
from src.riot.endpoints import MatchEndpoint

MATCH_BASE_URL = "/api/v1/matches"


class MatchEndpointV1Test(TestBase):
    def setUp(self):
        self.mock_service = MagicMock()
        endpoint = MatchEndpoint(self.mock_service)
        self.app = FastAPI()
        self.app.include_router(endpoint.router, prefix="/api/v1")
        for route in self.app.routes:
            for dep in getattr(route, 'dependencies', []):
                if isinstance(dep.dependency, JWTBearer):
                    self.app.dependency_overrides[dep.dependency] = lambda: {}
        disable_installed_extensions_check()
        add_pagination(self.app)
        self.client = TestClient(self.app)

    def test_get_matches_search_all(self):
        match_fixture = fixtures.match_fixture
        expected = match_fixture.model_dump()
        self.mock_service.get_matches.return_value = [match_fixture]

        response = self.client.get(MATCH_BASE_URL)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_matches_filter_by_league_slug(self):
        match_fixture = fixtures.match_fixture
        expected = match_fixture.model_dump()
        self.mock_service.get_matches.return_value = [match_fixture]

        response = self.client.get(
            f"{MATCH_BASE_URL}?league_slug={match_fixture.league_slug}"
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_matches_filter_by_tournament_id(self):
        match_fixture = fixtures.match_fixture
        expected = match_fixture.model_dump()
        self.mock_service.get_matches.return_value = [match_fixture]

        response = self.client.get(
            f"{MATCH_BASE_URL}?tournament_id={match_fixture.tournament_id}"
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_match_by_id_success(self):
        match_fixture = fixtures.match_fixture
        expected = match_fixture.model_dump()
        self.mock_service.get_match_by_id.return_value = match_fixture

        response = self.client.get(f"{MATCH_BASE_URL}/{match_fixture.id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected, response.json())

    def test_get_match_by_id_not_found(self):
        match_fixture = fixtures.match_fixture
        self.mock_service.get_match_by_id.side_effect = MatchNotFoundException()

        response = self.client.get(f"{MATCH_BASE_URL}/{match_fixture.id}")

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
