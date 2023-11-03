from fastapi.testclient import TestClient
from http import HTTPStatus

from tests.FantasyLolTestBase import FantasyLolTestBase
from tests.test_util.game_test_util import GameTestUtil
from tests.test_util.tournament_test_util import TournamentTestUtil
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import Game
from fantasylol.util.game_state import GameState
from fantasylol.main import app

GAME_BASE_URL = "/riot/v1/game"

class GameEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_tournament = TournamentTestUtil.create_active_tournament()

    def test_get_game_endpoint_completed_status(self):
        expected_game = GameTestUtil.create_completed_game(self.test_tournament.id)
        status = GameState.COMPLETED
        response = self.client.get(f"{GAME_BASE_URL}?status={status}")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(len(games), 1)

        game_from_request = Game(**games[0])
        self.assertEqual(game_from_request, expected_game)

    def test_get_game_endpoint_inprogress_status(self):
        expected_game = GameTestUtil.create_inprogress_game(self.test_tournament.id)
        status = GameState.INPROGRESS
        response = self.client.get(f"{GAME_BASE_URL}?status={status}")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(len(games), 1)

        game_from_request = Game(**games[0])
        self.assertEqual(game_from_request, expected_game)

    def test_get_game_endpoint_unstarted_status(self):
        expected_game = GameTestUtil.create_unstarted_game(self.test_tournament.id)
        status = GameState.UNSTARTED
        response = self.client.get(f"{GAME_BASE_URL}?status={status}")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(len(games), 1)

        game_from_request = Game(**games[0])
        self.assertEqual(game_from_request, expected_game)

    def test_get_game_endpoint_invalid_status(self):
        status = "invalid"
        response = self.client.get(f"{GAME_BASE_URL}?status={status}")

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        response_msg = response.json()
        self.assertIn("Invalid status value", response_msg['detail'])

    def test_get_game_by_block_filter_existing_game(self):
        expected_game = GameTestUtil.create_inprogress_game(self.test_tournament.id)
        block_name = expected_game.block_name
        response = self.client.get(f"{GAME_BASE_URL}?block={block_name}")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(len(games), 1)

        game_from_request = Game(**games[0])
        self.assertEqual(game_from_request, expected_game)

    def test_get_game_by_block_filter_no_existing_game(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        block_name = "badBlockName"
        response = self.client.get(f"{GAME_BASE_URL}?block={block_name}")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(len(games), 0)

    def test_get_game_by_tournament_filter_existing_game(self):
        expected_game = GameTestUtil.create_inprogress_game(self.test_tournament.id)
        tournament_id = expected_game.tournament_id
        response = self.client.get(f"{GAME_BASE_URL}?tournament={tournament_id}")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(len(games), 1)

        game_from_request = Game(**games[0])
        self.assertEqual(game_from_request, expected_game)

    def test_get_game_by_tournament_filter_no_existing_game(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        tournament_id = 777
        response = self.client.get(f"{GAME_BASE_URL}?block={tournament_id}")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        games = response.json()
        self.assertIsInstance(games, list)
        self.assertEqual(len(games), 0)

    def test_get_game_by_id_endpoint_success(self):
        expected_game = GameTestUtil.create_inprogress_game(self.test_tournament.id)
        game_id = expected_game.id
        response = self.client.get(f"{GAME_BASE_URL}/{game_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        game = response.json()
        self.assertIsInstance(game, dict)

        game_from_request = Game(**game)
        self.assertEqual(game_from_request, expected_game)

    def test_get_game_by_id_endpoint_not_found(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        game_id = 777
        response = self.client.get(f"{GAME_BASE_URL}/{game_id}")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response_msg = response.json()
        self.assertIn("Game not found", response_msg['detail'])
