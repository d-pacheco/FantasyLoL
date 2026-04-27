from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from http import HTTPStatus
from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import riot_fixtures as fixtures

from src.auth import JWTBearer
from src.common.schemas.riot_data_schemas import TournamentStatus
from src.riot.exceptions import TournamentNotFoundException
from src.riot.endpoints import TournamentEndpoint

TOURNAMENT_BASE_URL = "/api/v1/tournament"


class TournamentEndpointV1Test(TestBase):
    def setUp(self):
        self.mock_service = MagicMock()
        endpoint = TournamentEndpoint(self.mock_service)
        self.app = FastAPI()
        self.app.include_router(endpoint.router, prefix="/api/v1")
        for route in self.app.routes:
            for dep in getattr(route, 'dependencies', []):
                if isinstance(dep.dependency, JWTBearer):
                    self.app.dependency_overrides[dep.dependency] = lambda: {}
        disable_installed_extensions_check()
        add_pagination(self.app)
        self.client = TestClient(self.app)

    def test_get_tournaments_active(self):
        tournament_fixture = fixtures.active_tournament_fixture
        expected = tournament_fixture.model_dump()
        self.mock_service.get_tournaments.return_value = [tournament_fixture]

        response = self.client.get(
            f"{TOURNAMENT_BASE_URL}?status={TournamentStatus.ACTIVE.value}"
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_tournaments_completed(self):
        tournament_fixture = fixtures.tournament_fixture
        expected = tournament_fixture.model_dump()
        self.mock_service.get_tournaments.return_value = [tournament_fixture]

        response = self.client.get(
            f"{TOURNAMENT_BASE_URL}?status={TournamentStatus.COMPLETED.value}"
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_tournaments_upcoming(self):
        tournament_fixture = fixtures.future_tournament_fixture
        expected = tournament_fixture.model_dump()
        self.mock_service.get_tournaments.return_value = [tournament_fixture]

        response = self.client.get(
            f"{TOURNAMENT_BASE_URL}?status={TournamentStatus.UPCOMING.value}"
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        items = response.json().get('items')
        self.assertEqual(1, len(items))
        self.assertEqual(expected, items[0])

    def test_get_tournaments_invalid_status(self):
        response = self.client.get(f"{TOURNAMENT_BASE_URL}?status=invalid")
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)

    def test_get_tournament_by_id_success(self):
        tournament_fixture = fixtures.tournament_fixture
        expected = tournament_fixture.model_dump()
        self.mock_service.get_tournament_by_id.return_value = tournament_fixture

        response = self.client.get(f"{TOURNAMENT_BASE_URL}/{tournament_fixture.id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected, response.json())

    def test_get_tournament_by_id_not_found(self):
        tournament_fixture = fixtures.tournament_fixture
        self.mock_service.get_tournament_by_id.side_effect = TournamentNotFoundException()

        response = self.client.get(f"{TOURNAMENT_BASE_URL}/{tournament_fixture.id}")

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
