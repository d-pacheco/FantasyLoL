from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from http import HTTPStatus
from unittest.mock import patch

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import test_fixtures as fixtures

from riot.exceptions.game_not_found_exception import GameNotFoundException
from common.schemas.riot_data_schemas import GameState
from common.schemas.search_parameters import GameSearchParameters
from riot import app

GAME_BASE_URL = "/riot/v1/game"
BASE_GAME_SERVICE_MOCK_PATH = "riot.service.riot_game_service.RiotGameService"
GET_GAMES_MOCK_PATH = f"{BASE_GAME_SERVICE_MOCK_PATH}.get_games"
GET_GAME_BY_ID_MOCK_PATH = f"{BASE_GAME_SERVICE_MOCK_PATH}.get_game_by_id"


class GameEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        add_pagination(app)
        self.client = TestClient(app)

    @patch(GET_GAMES_MOCK_PATH)
    def test_get_game_endpoint_completed_status(self, mock_get_games):
        # Arrange
        game_fixture = fixtures.game_1_fixture_completed
        expected_game_response = game_fixture.model_dump()
        mock_get_games.return_value = [game_fixture]
        state = GameState.COMPLETED.value

        # Act
        response = self.client.get(f"{GAME_BASE_URL}?state={state}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        games = response_json.get('items')
        self.assertIsInstance(games, list)
        self.assertEqual(1, len(games))
        self.assertEqual(expected_game_response, games[0])
        mock_get_games.assert_called_once_with(
            GameSearchParameters(state=state)
        )

    @patch(GET_GAMES_MOCK_PATH)
    def test_get_game_endpoint_inprogress_status(self, mock_get_games):
        # Arrange
        game_fixture = fixtures.game_2_fixture_inprogress
        expected_game_response = game_fixture.model_dump()
        mock_get_games.return_value = [game_fixture]
        state = GameState.INPROGRESS.value

        # Act
        response = self.client.get(f"{GAME_BASE_URL}?state={state}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        games = response_json.get('items')
        self.assertIsInstance(games, list)
        self.assertEqual(1, len(games))
        self.assertEqual(expected_game_response, games[0])
        mock_get_games.assert_called_once_with(GameSearchParameters(state=state))

    @patch(GET_GAMES_MOCK_PATH)
    def test_get_game_endpoint_unstarted_status(self, mock_get_games):
        # Arrange
        game_fixture = fixtures.game_3_fixture_unstarted
        expected_game_response = game_fixture.model_dump()
        mock_get_games.return_value = [game_fixture]
        state = GameState.UNSTARTED.value

        # Act
        response = self.client.get(f"{GAME_BASE_URL}?state={state}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        games = response_json.get('items')
        self.assertIsInstance(games, list)
        self.assertEqual(1, len(games))
        self.assertEqual(expected_game_response, games[0])
        mock_get_games.assert_called_once_with(GameSearchParameters(state=state))

    @patch(GET_GAMES_MOCK_PATH)
    def test_get_game_endpoint_unneeded_status(self, mock_get_games):
        # Arrange
        game_fixture = fixtures.game_4_fixture_unneeded
        expected_game_response = game_fixture.model_dump()
        mock_get_games.return_value = [game_fixture]
        state = GameState.UNSTARTED.value

        # Act
        response = self.client.get(f"{GAME_BASE_URL}?state={state}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        games = response_json.get('items')
        self.assertIsInstance(games, list)
        self.assertEqual(1, len(games))
        self.assertEqual(expected_game_response, games[0])
        mock_get_games.assert_called_once_with(GameSearchParameters(state=state))

    @patch(GET_GAMES_MOCK_PATH)
    def test_get_game_endpoint_invalid_status(self, mock_get_games):
        # Arrange
        status = "invalid"

        # Act
        response = self.client.get(f"{GAME_BASE_URL}?state={status}")

        # Assert
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)
        mock_get_games.assert_not_called()

    @patch(GET_GAMES_MOCK_PATH)
    def test_get_game_endpoint_by_tournament_filter_existing_game(self, mock_get_games):
        # Arrange
        game_fixture = fixtures.game_1_fixture_completed
        expected_game_response = game_fixture.model_dump()
        mock_get_games.return_value = [game_fixture]

        # Act
        response = self.client.get(
            f"{GAME_BASE_URL}?match_id={game_fixture.match_id}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        games = response_json.get('items')
        self.assertIsInstance(games, list)
        self.assertEqual(1, len(games))
        self.assertEqual(expected_game_response, games[0])
        mock_get_games.assert_called_once_with(
            GameSearchParameters(match_id=game_fixture.match_id)
        )

    @patch(GET_GAME_BY_ID_MOCK_PATH)
    def test_get_game_by_id_endpoint_success(self, mock_get_game_by_id):
        # Arrange
        game_fixture = fixtures.game_1_fixture_completed
        expected_game_response = game_fixture.model_dump()
        mock_get_game_by_id.return_value = game_fixture

        # Act
        response = self.client.get(f"{GAME_BASE_URL}/{game_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        game = response.json()
        self.assertIsInstance(game, dict)
        self.assertEqual(expected_game_response, game)
        mock_get_game_by_id.assert_called_once_with(game_fixture.id)

    @patch(GET_GAME_BY_ID_MOCK_PATH)
    def test_get_game_by_id_endpoint_not_found(self, mock_get_game_by_id):
        # Arrange
        game_id = "777"
        mock_get_game_by_id.side_effect = GameNotFoundException

        # Act
        response = self.client.get(f"{GAME_BASE_URL}/{game_id}")

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_game_by_id.assert_called_once_with(game_id)
