from http import HTTPStatus
from unittest.mock import Mock, patch

from tests.fantasy_lol_test_base import FantasyLolTestBase, RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from tests.riot_api_requester_util import RiotApiRequestUtil
from tests.test_util.tournament_test_util import TournamentTestUtil
from tests.test_util.game_test_util import GameTestUtil
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import Game
from fantasylol.exceptions.riot_api_status_code_assert_exception import \
    RiotApiStatusCodeAssertException
from fantasylol.exceptions.game_not_found_exception import GameNotFoundException
from fantasylol.service.riot_game_service import RiotGameService
from fantasylol.schemas.game_state import GameState


class GameServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()
        self.test_tournament = TournamentTestUtil.create_active_tournament()

    def create_game_service(self):
        return RiotGameService()

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_live_games_successful(self, mock_create_scraper):
        expected_json = self.riot_api_util.create_mock_live_game_response()
        expected_game = self.riot_api_util.create_mock_game()

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        game_service = self.create_game_service()
        game_service.fetch_and_store_live_games()

        with DatabaseConnection() as db:
            game_from_db = db.query(Game).filter_by(id=expected_game.id).first()
        self.assertEqual(game_from_db, expected_game)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_live_games_fail(self, mock_create_scraper):

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        # Create an instance of RiotApiService and call the method to test
        game_service = self.create_game_service()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            game_service.fetch_and_store_live_games()

    def test_get_completed_games(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        GameTestUtil.create_unstarted_game(self.test_tournament.id)
        expected_game = GameTestUtil.create_completed_game(self.test_tournament.id)
        query_params = {"state": GameState.COMPLETED}

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(query_params)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 1)
        self.assertEqual(games_from_db[0], expected_game)

    def test_get_completed_games_with_no_completed_games(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        GameTestUtil.create_unstarted_game(self.test_tournament.id)
        query_params = {"state": GameState.COMPLETED}

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(query_params)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 0)

    def test_get_inprogress_games(self):
        GameTestUtil.create_unstarted_game(self.test_tournament.id)
        GameTestUtil.create_completed_game(self.test_tournament.id)
        expected_game = GameTestUtil.create_inprogress_game(self.test_tournament.id)
        query_params = {"state": GameState.INPROGRESS}

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(query_params)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 1)
        self.assertEqual(games_from_db[0], expected_game)

    def test_get_inprogress_games_with_no_inprogress_games(self):
        GameTestUtil.create_completed_game(self.test_tournament.id)
        GameTestUtil.create_unstarted_game(self.test_tournament.id)
        query_params = {"state": GameState.INPROGRESS}

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(query_params)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 0)

    def test_get_unstarted_games(self):
        GameTestUtil.create_completed_game(self.test_tournament.id)
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        expected_game = GameTestUtil.create_unstarted_game(self.test_tournament.id)
        query_params = {"state": GameState.UNSTARTED}

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(query_params)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 1)
        self.assertEqual(games_from_db[0], expected_game)

    def test_get_unstarted_games_with_no_unstarted_games(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        GameTestUtil.create_completed_game(self.test_tournament.id)
        query_params = {"state": GameState.UNSTARTED}

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(query_params)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 0)

    def test_get_games_by_match_id_existing_games(self):
        expected_game = GameTestUtil.create_inprogress_game(self.test_tournament.id)
        query_params = {"match_id": expected_game.match_id}

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(query_params)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 1)
        self.assertEqual(games_from_db[0], expected_game)

    def test_get_games_by_match_id_no_existing_games(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        query_params = {"match_id": 777}

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(query_params)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 0)

    def test_get_game_by_id_valid_id(self):
        expected_game = GameTestUtil.create_inprogress_game(self.test_tournament.id)
        game_service = self.create_game_service()
        game_from_db = game_service.get_game_by_id(expected_game.id)
        self.assertEqual(expected_game, game_from_db)

    def test_get_game_by_id_invalid_id(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        game_service = self.create_game_service()
        with self.assertRaises(GameNotFoundException):
            game_service.get_game_by_id(777)
