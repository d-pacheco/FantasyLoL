from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from http import HTTPStatus

from tests.test_base import FantasyLolTestBase
from tests.test_util import riot_fixtures as fixtures

from src.riot.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from src.common.schemas.search_parameters import PlayerSearchParameters
from src.riot import app

PROFESSIONAL_PLAYER_BASE_URL = "/riot/v1/professional-player"
BASE_PLAYER_SERVICE_MOCK_PATH = \
    "src.riot.service.riot_professional_player_service.RiotProfessionalPlayerService"
PLAYER_SERVICE_GET_PLAYERS_MOCK_PATH = f"{BASE_PLAYER_SERVICE_MOCK_PATH}.get_players"
PLAYER_SERVICE_GET_PLAYER_BY_ID_MOCK_PATH = f"{BASE_PLAYER_SERVICE_MOCK_PATH}.get_player_by_id"


class ProfessionalPlayerEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        add_pagination(app)
        self.client = TestClient(app)

    @patch(PLAYER_SERVICE_GET_PLAYERS_MOCK_PATH)
    def test_get_professional_players_endpoint_summoner_name_query(self, mock_get_players):
        # Arrange
        player_fixture = fixtures.player_1_fixture
        expected_player_response = player_fixture.model_dump()
        mock_get_players.return_value = [player_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_PLAYER_BASE_URL}?summoner_name={player_fixture.summoner_name}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        professional_players = response_json.get('items')
        self.assertIsInstance(professional_players, list)
        self.assertEqual(1, len(professional_players))
        self.assertEqual(expected_player_response, professional_players[0])
        mock_get_players.assert_called_once_with(
            PlayerSearchParameters(summoner_name=player_fixture.summoner_name)
        )

    @patch(PLAYER_SERVICE_GET_PLAYERS_MOCK_PATH)
    def test_get_professional_players_endpoint_role_query(self, mock_get_players):
        # Arrange
        player_fixture = fixtures.player_1_fixture
        expected_player_response = player_fixture.model_dump()
        mock_get_players.return_value = [player_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_PLAYER_BASE_URL}?role={player_fixture.role}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        professional_players = response_json.get('items')
        self.assertIsInstance(professional_players, list)
        self.assertEqual(1, len(professional_players))
        self.assertEqual(expected_player_response, professional_players[0])
        mock_get_players.assert_called_once_with(
            PlayerSearchParameters(role=player_fixture.role)
        )

    @patch(PLAYER_SERVICE_GET_PLAYERS_MOCK_PATH)
    def test_get_professional_players_endpoint_team_id_query(self, mock_get_players):
        # Arrange
        player_fixture = fixtures.player_1_fixture
        expected_player_response = player_fixture.model_dump()
        mock_get_players.return_value = [player_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_PLAYER_BASE_URL}?team_id={player_fixture.team_id}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        professional_players = response_json.get('items')
        self.assertIsInstance(professional_players, list)
        self.assertEqual(1, len(professional_players))
        self.assertEqual(expected_player_response, professional_players[0])
        mock_get_players.assert_called_once_with(
            PlayerSearchParameters(team_id=player_fixture.team_id)
        )

    @patch(PLAYER_SERVICE_GET_PLAYERS_MOCK_PATH)
    def test_get_professional_players_endpoint_search_all(self, mock_get_players):
        # Arrange
        player_fixture = fixtures.player_1_fixture
        expected_player_response = player_fixture.model_dump()
        mock_get_players.return_value = [player_fixture]

        # Act
        response = self.client.get(f"{PROFESSIONAL_PLAYER_BASE_URL}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        professional_players = response_json.get('items')
        self.assertIsInstance(professional_players, list)
        self.assertEqual(1, len(professional_players))
        self.assertEqual(expected_player_response, professional_players[0])
        mock_get_players.assert_called_once_with(PlayerSearchParameters())

    @patch(PLAYER_SERVICE_GET_PLAYER_BY_ID_MOCK_PATH)
    def test_get_professional_players_endpoint_by_id(self, mock_get_player_by_id):
        # Arrange
        player_fixture = fixtures.player_1_fixture
        expected_player_response = player_fixture.model_dump()
        mock_get_player_by_id.return_value = player_fixture

        # Act
        response = self.client.get(f"{PROFESSIONAL_PLAYER_BASE_URL}/{player_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        professional_player = response.json()
        self.assertIsInstance(professional_player, dict)
        self.assertEqual(expected_player_response, professional_player)
        mock_get_player_by_id.assert_called_once_with(player_fixture.id)

    @patch(PLAYER_SERVICE_GET_PLAYER_BY_ID_MOCK_PATH)
    def test_get_professional_players_endpoint_by_id_not_found(self, mock_get_player_by_id):
        # Arrange
        player_fixture = fixtures.player_1_fixture
        mock_get_player_by_id.side_effect = ProfessionalPlayerNotFoundException

        # Act
        response = self.client.get(f"{PROFESSIONAL_PLAYER_BASE_URL}/{player_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_player_by_id.assert_called_once_with(player_fixture.id)
