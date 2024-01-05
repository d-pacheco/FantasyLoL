from fastapi.testclient import TestClient
from unittest.mock import patch
from http import HTTPStatus

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util.tournament_test_util import TournamentTestUtil
from fantasylol.exceptions.tournament_not_found_exception import \
    TournamentNotFoundException
from fantasylol.schemas.tournament_status import TournamentStatus
from fantasylol.schemas.riot_data_schemas import TournamentSchema
from fantasylol.schemas.search_parameters import TournamentSearchParameters
from fantasylol import app


TOURNAMENT_BASE_URL = "/riot/v1/tournament"
BASE_TOURNAMENT_SERVICE_MOCK_PATH = \
    "fantasylol.service.riot_tournament_service.RiotTournamentService"
GET_TOURNAMENTS_MOCK_PATH = f"{BASE_TOURNAMENT_SERVICE_MOCK_PATH}.get_tournaments"
GET_TOURNAMENTS_BY_ID_MOCK_PATH = f"{BASE_TOURNAMENT_SERVICE_MOCK_PATH}.get_tournament_by_id"


class TournamentEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        self.client = TestClient(app)

    @patch(GET_TOURNAMENTS_MOCK_PATH)
    def test_get_tournaments_endpoint_active(self, mock_get_tournaments):
        # Arrange
        tournament_db_fixture = TournamentTestUtil.create_active_tournament()
        expected_tournament_response_schema = TournamentSchema(**tournament_db_fixture.to_dict())
        mock_get_tournaments.return_value = [tournament_db_fixture]
        status = TournamentStatus.ACTIVE.value

        # Act
        response = self.client.get(f"{TOURNAMENT_BASE_URL}?status={status}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        tournaments = response.json()
        self.assertIsInstance(tournaments, list)
        self.assertEqual(1, len(tournaments))
        tournament_response_schema = TournamentSchema(**tournaments[0])
        self.assertEqual(expected_tournament_response_schema, tournament_response_schema)
        mock_get_tournaments.assert_called_once_with(TournamentSearchParameters(status=status))

    @patch(GET_TOURNAMENTS_MOCK_PATH)
    def test_get_tournaments_endpoint_completed(self, mock_get_tournaments):
        # Arrange
        tournament_db_fixture = TournamentTestUtil.create_completed_tournament()
        expected_tournament_response_schema = TournamentSchema(**tournament_db_fixture.to_dict())
        mock_get_tournaments.return_value = [tournament_db_fixture]
        status = TournamentStatus.COMPLETED.value

        # Act
        response = self.client.get(f"{TOURNAMENT_BASE_URL}?status={status}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        tournaments = response.json()
        self.assertIsInstance(tournaments, list)
        self.assertEqual(1, len(tournaments))
        tournament_response_schema = TournamentSchema(**tournaments[0])
        self.assertEqual(expected_tournament_response_schema, tournament_response_schema)
        mock_get_tournaments.assert_called_once_with(TournamentSearchParameters(status=status))

    @patch(GET_TOURNAMENTS_MOCK_PATH)
    def test_get_tournaments_endpoint_upcoming(self, mock_get_tournaments):
        # Arrange
        tournament_db_fixture = TournamentTestUtil.create_upcoming_tournament()
        expected_tournament_response_schema = TournamentSchema(**tournament_db_fixture.to_dict())
        mock_get_tournaments.return_value = [tournament_db_fixture]
        status = TournamentStatus.UPCOMING.value

        # Act
        response = self.client.get(f"{TOURNAMENT_BASE_URL}?status={status}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        tournaments = response.json()
        self.assertIsInstance(tournaments, list)
        self.assertEqual(1, len(tournaments))
        tournament_response_schema = TournamentSchema(**tournaments[0])
        self.assertEqual(expected_tournament_response_schema, tournament_response_schema)
        mock_get_tournaments.assert_called_once_with(TournamentSearchParameters(status=status))

    def test_get_tournaments_endpoint_invalid(self):
        status = "invalid"
        response = self.client.get(f"{TOURNAMENT_BASE_URL}?status={status}")
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)

    @patch(GET_TOURNAMENTS_BY_ID_MOCK_PATH)
    def test_get_tournament_by_id_success(self, mock_get_tournament_by_id):
        # Arrange
        tournament_db_fixture = TournamentTestUtil.create_upcoming_tournament()
        expected_tournament_response_schema = TournamentSchema(**tournament_db_fixture.to_dict())
        mock_get_tournament_by_id.return_value = tournament_db_fixture

        # Act
        response = self.client.get(f"{TOURNAMENT_BASE_URL}/{tournament_db_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        tournament = response.json()
        self.assertIsInstance(tournament, dict)
        tournament_response_schema = TournamentSchema(**tournament)
        self.assertEqual(expected_tournament_response_schema, tournament_response_schema)
        mock_get_tournament_by_id.assert_called_once_with(tournament_db_fixture.id)

    @patch(GET_TOURNAMENTS_BY_ID_MOCK_PATH)
    def test_get_tournament_by_id_with_not_found(self, mock_get_tournament_by_id):
        # Arrange
        tournament_db_fixture = TournamentTestUtil.create_upcoming_tournament()
        mock_get_tournament_by_id.side_effect = TournamentNotFoundException

        # Act
        response = self.client.get(f"{TOURNAMENT_BASE_URL}/{tournament_db_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_tournament_by_id.assert_called_once_with(tournament_db_fixture.id)
