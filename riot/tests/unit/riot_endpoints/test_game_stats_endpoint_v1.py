from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from http import HTTPStatus
from unittest.mock import patch

from ...test_base import FantasyLolTestBase
from tests.test_util import test_fixtures as fixtures

from common.schemas.search_parameters import PlayerGameStatsSearchParameters
from riot import app

GAME_STATS_BASE_URL = "/riot/v1/stats"
BASE_GAME_STATS_SERVICE_MOCK_PATH = \
    "riot.service.riot_game_stats_service.RiotGameStatsService"
GET_PLAYER_GAME_STATS_MOCK_PATH = f"{BASE_GAME_STATS_SERVICE_MOCK_PATH}.get_player_stats"


class GameStatsEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        add_pagination(app)
        self.client = TestClient(app)

    @patch(GET_PLAYER_GAME_STATS_MOCK_PATH)
    def test_get_player_stats_endpoint_no_filters_existing_data(self, mock_get_player_stats):
        # Arrange
        player_game_data_fixture = fixtures.player_1_game_data_fixture
        expected_player_game_data_response = player_game_data_fixture.model_dump()
        mock_get_player_stats.return_value = [player_game_data_fixture]

        # Act
        response = self.client.get(f"{GAME_STATS_BASE_URL}/player")

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_json: dict = response.json()
        player_game_data = response_json.get('items')
        self.assertIsInstance(player_game_data, list)
        self.assertEqual(1, len(player_game_data))
        self.assertEqual(expected_player_game_data_response, player_game_data[0])
        mock_get_player_stats.assert_called_once_with(
            PlayerGameStatsSearchParameters()
        )

    @patch(GET_PLAYER_GAME_STATS_MOCK_PATH)
    def test_get_player_stats_endpoint_no_filters_no_existing_data(self, mock_get_player_stats):
        # Arrange
        mock_get_player_stats.return_value = []

        # Act
        response = self.client.get(f"{GAME_STATS_BASE_URL}/player")

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_json: dict = response.json()
        player_game_data = response_json.get('items')
        self.assertIsInstance(player_game_data, list)
        self.assertEqual(0, len(player_game_data))
        mock_get_player_stats.assert_called_once_with(
            PlayerGameStatsSearchParameters()
        )

    @patch(GET_PLAYER_GAME_STATS_MOCK_PATH)
    def test_get_player_stats_endpoint_filter_by_game_id_existing_data(
            self, mock_get_player_stats):
        # Arrange
        player_game_data_fixture = fixtures.player_1_game_data_fixture
        expected_player_game_data_response = player_game_data_fixture.model_dump()
        mock_get_player_stats.return_value = [player_game_data_fixture]

        # Act
        response = self.client.get(
            f"{GAME_STATS_BASE_URL}/player?game_id={player_game_data_fixture.game_id}"
        )

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_json: dict = response.json()
        player_game_data = response_json.get('items')
        self.assertIsInstance(player_game_data, list)
        self.assertEqual(1, len(player_game_data))
        self.assertEqual(expected_player_game_data_response, player_game_data[0])
        mock_get_player_stats.assert_called_once_with(
            PlayerGameStatsSearchParameters(
                game_id=player_game_data_fixture.game_id
            )
        )

    @patch(GET_PLAYER_GAME_STATS_MOCK_PATH)
    def test_get_player_stats_endpoint_filter_by_game_id_no_existing_data(
            self, mock_get_player_stats):
        # Arrange
        player_game_data_fixture = fixtures.player_1_game_data_fixture
        mock_get_player_stats.return_value = []

        # Act
        response = self.client.get(
            f"{GAME_STATS_BASE_URL}/player?game_id={player_game_data_fixture.game_id}"
        )

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_json: dict = response.json()
        player_game_data = response_json.get('items')
        self.assertIsInstance(player_game_data, list)
        self.assertEqual(0, len(player_game_data))
        mock_get_player_stats.assert_called_once_with(
            PlayerGameStatsSearchParameters(
                game_id=player_game_data_fixture.game_id
            )
        )

    @patch(GET_PLAYER_GAME_STATS_MOCK_PATH)
    def test_get_player_stats_endpoint_filter_by_player_id_existing_data(
            self, mock_get_player_stats):
        # Arrange
        player_game_data_fixture = fixtures.player_1_game_data_fixture
        expected_player_game_data_response = player_game_data_fixture.model_dump()
        mock_get_player_stats.return_value = [player_game_data_fixture]

        # Act
        response = self.client.get(
            f"{GAME_STATS_BASE_URL}/player?player_id={player_game_data_fixture.player_id}"
        )

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_json: dict = response.json()
        player_game_data = response_json.get('items')
        self.assertIsInstance(player_game_data, list)
        self.assertEqual(1, len(player_game_data))
        self.assertEqual(expected_player_game_data_response, player_game_data[0])
        mock_get_player_stats.assert_called_once_with(
            PlayerGameStatsSearchParameters(
                player_id=player_game_data_fixture.player_id
            )
        )

    @patch(GET_PLAYER_GAME_STATS_MOCK_PATH)
    def test_get_player_stats_endpoint_filter_by_player_id_no_existing_data(
            self, mock_get_player_stats):
        # Arrange
        player_game_data_fixture = fixtures.player_1_game_data_fixture
        mock_get_player_stats.return_value = []

        # Act
        response = self.client.get(
            f"{GAME_STATS_BASE_URL}/player?player_id={player_game_data_fixture.player_id}"
        )

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_json: dict = response.json()
        player_game_data = response_json.get('items')
        self.assertIsInstance(player_game_data, list)
        self.assertEqual(0, len(player_game_data))
        mock_get_player_stats.assert_called_once_with(
            PlayerGameStatsSearchParameters(
                player_id=player_game_data_fixture.player_id
            )
        )
