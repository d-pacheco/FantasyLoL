from fastapi.testclient import TestClient
from http import HTTPStatus
from unittest.mock import patch

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util.game_test_util import GameTestUtil
from tests.test_util.tournament_test_util import TournamentTestUtil
from fantasylol.exceptions.game_not_found_exception import GameNotFoundException
from fantasylol.schemas.game_state import GameState
from fantasylol.schemas.riot_data_schemas import GameSchema
from fantasylol.schemas.search_parameters import GameSearchParameters
from fantasylol import app

GAME_BASE_URL = "/riot/v1/game"
BASE_GAME_SERVICE_MOCK_PATH = "fantasylol.service.riot_game_service.RiotGameService"
GET_GAMES_MOCK_PATH = f"{BASE_GAME_SERVICE_MOCK_PATH}.get_games"
GET_GAME_BY_ID_MOCK_PATH = f"{BASE_GAME_SERVICE_MOCK_PATH}.get_game_by_id"


class GameEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_tournament = TournamentTestUtil.create_active_tournament()

    @patch(GET_GAMES_MOCK_PATH)
    def test_get_game_endpoint_completed_status(self, mock_get_games):
        # Arrange
        game_db_fixture = GameTestUtil.create_completed_game(self.test_tournament.id)
        expected_game_response_schema = GameSchema(**game_db_fixture.to_dict())
        mock_get_games.return_value = [game_db_fixture]
        state = GameState.COMPLETED.value

        # Act
        response = self.client.get(f"{GAME_BASE_URL}?state={state}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(1, len(games))
        game_response_schema = GameSchema(**games[0])
        self.assertEqual(expected_game_response_schema, game_response_schema)
        mock_get_games.assert_called_once_with(
            GameSearchParameters(state=state)
        )

    @patch(GET_GAMES_MOCK_PATH)
    def test_get_game_endpoint_inprogress_status(self, mock_get_games):
        # Arrange
        game_db_fixture = GameTestUtil.create_inprogress_game(self.test_tournament.id)
        expected_game_response_schema = GameSchema(**game_db_fixture.to_dict())
        mock_get_games.return_value = [game_db_fixture]
        state = GameState.INPROGRESS.value

        # Act
        response = self.client.get(f"{GAME_BASE_URL}?state={state}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(1, len(games))
        game_response_schema = GameSchema(**games[0])
        self.assertEqual(expected_game_response_schema, game_response_schema)
        mock_get_games.assert_called_once_with(GameSearchParameters(state=state))

    @patch(GET_GAMES_MOCK_PATH)
    def test_get_game_endpoint_unstarted_status(self, mock_get_games):
        # Arrange
        game_db_fixture = GameTestUtil.create_unstarted_game(self.test_tournament.id)
        expected_game_response_schema = GameSchema(**game_db_fixture.to_dict())
        mock_get_games.return_value = [game_db_fixture]
        state = GameState.UNSTARTED.value

        # Act
        response = self.client.get(f"{GAME_BASE_URL}?state={state}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(1, len(games))
        game_response_schema = GameSchema(**games[0])
        self.assertEqual(expected_game_response_schema, game_response_schema)
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
        game_db_fixture = GameTestUtil.create_completed_game(self.test_tournament.id)
        expected_game_response_schema = GameSchema(**game_db_fixture.to_dict())
        mock_get_games.return_value = [game_db_fixture]

        # Act
        response = self.client.get(
            f"{GAME_BASE_URL}?match_id={game_db_fixture.match_id}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(1, len(games))
        game_response_schema = GameSchema(**games[0])
        self.assertEqual(expected_game_response_schema, game_response_schema)
        mock_get_games.assert_called_once_with(
            GameSearchParameters(match_id=game_db_fixture.match_id)
        )

    @patch(GET_GAME_BY_ID_MOCK_PATH)
    def test_get_game_by_id_endpoint_success(self, mock_get_game_by_id):
        # Arrange
        game_db_fixture = GameTestUtil.create_completed_game(self.test_tournament.id)
        expected_game_response_schema = GameSchema(**game_db_fixture.to_dict())
        mock_get_game_by_id.return_value = game_db_fixture

        # Act
        response = self.client.get(f"{GAME_BASE_URL}/{game_db_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        game = response.json()
        self.assertIsInstance(game, dict)
        game_response_schema = GameSchema(**game)
        self.assertEqual(expected_game_response_schema, game_response_schema)
        mock_get_game_by_id.assert_called_once_with(game_db_fixture.id)

    @patch(GET_GAME_BY_ID_MOCK_PATH)
    def test_get_game_by_id_endpoint_not_found(self, mock_get_game_by_id):
        # Arrange
        game_id = 777
        mock_get_game_by_id.side_effect = GameNotFoundException

        # Act
        response = self.client.get(f"{GAME_BASE_URL}/{game_id}")

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_game_by_id.assert_called_once_with(game_id)
