from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from unittest.mock import patch
from http import HTTPStatus

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import test_fixtures as fixtures

from riot.exceptions.tournament_not_found_exception import \
    TournamentNotFoundException
from common.schemas.riot_data_schemas import TournamentStatus
from common.schemas.search_parameters import TournamentSearchParameters
from riot import app


TOURNAMENT_BASE_URL = "/riot/v1/tournament"
BASE_TOURNAMENT_SERVICE_MOCK_PATH = \
    "riot.service.riot_tournament_service.RiotTournamentService"
GET_TOURNAMENTS_MOCK_PATH = f"{BASE_TOURNAMENT_SERVICE_MOCK_PATH}.get_tournaments"
GET_TOURNAMENTS_BY_ID_MOCK_PATH = f"{BASE_TOURNAMENT_SERVICE_MOCK_PATH}.get_tournament_by_id"


class TournamentEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        add_pagination(app)
        self.client = TestClient(app)

    @patch(GET_TOURNAMENTS_MOCK_PATH)
    def test_get_tournaments_endpoint_active(self, mock_get_tournaments):
        # Arrange
        tournament_fixture = fixtures.active_tournament_fixture
        expected_tournament_response = tournament_fixture.model_dump()
        mock_get_tournaments.return_value = [tournament_fixture]
        status = TournamentStatus.ACTIVE.value

        # Act
        response = self.client.get(f"{TOURNAMENT_BASE_URL}?status={status}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        tournaments = response_json.get('items')
        self.assertIsInstance(tournaments, list)
        self.assertEqual(1, len(tournaments))
        self.assertEqual(expected_tournament_response, tournaments[0])
        mock_get_tournaments.assert_called_once_with(TournamentSearchParameters(status=status))

    @patch(GET_TOURNAMENTS_MOCK_PATH)
    def test_get_tournaments_endpoint_completed(self, mock_get_tournaments):
        # Arrange
        tournament_fixture = fixtures.tournament_fixture
        expected_tournament_response = tournament_fixture.model_dump()
        mock_get_tournaments.return_value = [tournament_fixture]
        status = TournamentStatus.COMPLETED.value

        # Act
        response = self.client.get(f"{TOURNAMENT_BASE_URL}?status={status}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        tournaments = response_json.get('items')
        self.assertIsInstance(tournaments, list)
        self.assertEqual(1, len(tournaments))
        self.assertEqual(expected_tournament_response, tournaments[0])
        mock_get_tournaments.assert_called_once_with(TournamentSearchParameters(status=status))

    @patch(GET_TOURNAMENTS_MOCK_PATH)
    def test_get_tournaments_endpoint_upcoming(self, mock_get_tournaments):
        # Arrange
        tournament_fixture = fixtures.future_tournament_fixture
        expected_tournament_response = tournament_fixture.model_dump()
        mock_get_tournaments.return_value = [tournament_fixture]
        status = TournamentStatus.UPCOMING.value

        # Act
        response = self.client.get(f"{TOURNAMENT_BASE_URL}?status={status}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        tournaments = response_json.get('items')
        self.assertIsInstance(tournaments, list)
        self.assertEqual(1, len(tournaments))
        self.assertEqual(expected_tournament_response, tournaments[0])
        mock_get_tournaments.assert_called_once_with(TournamentSearchParameters(status=status))

    def test_get_tournaments_endpoint_invalid(self):
        status = "invalid"
        response = self.client.get(f"{TOURNAMENT_BASE_URL}?status={status}")
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)

    @patch(GET_TOURNAMENTS_BY_ID_MOCK_PATH)
    def test_get_tournament_by_id_success(self, mock_get_tournament_by_id):
        # Arrange
        tournament_fixture = fixtures.tournament_fixture
        expected_tournament_response = tournament_fixture.model_dump()
        mock_get_tournament_by_id.return_value = tournament_fixture

        # Act
        response = self.client.get(f"{TOURNAMENT_BASE_URL}/{tournament_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        tournament = response.json()
        self.assertIsInstance(tournament, dict)
        self.assertEqual(expected_tournament_response, tournament)
        mock_get_tournament_by_id.assert_called_once_with(tournament_fixture.id)

    @patch(GET_TOURNAMENTS_BY_ID_MOCK_PATH)
    def test_get_tournament_by_id_with_not_found(self, mock_get_tournament_by_id):
        # Arrange
        tournament_fixture = fixtures.tournament_fixture
        mock_get_tournament_by_id.side_effect = TournamentNotFoundException

        # Act
        response = self.client.get(f"{TOURNAMENT_BASE_URL}/{tournament_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_tournament_by_id.assert_called_once_with(tournament_fixture.id)
