from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.riot_api_requester_util import RiotApiRequestUtil
from tests.test_util.tournament_test_util import TournamentTestUtil
from tests.test_util.game_test_util import GameTestUtil
from fantasylol.exceptions.game_not_found_exception import GameNotFoundException
from fantasylol.service.riot_game_service import RiotGameService
from fantasylol.schemas.game_state import GameState
from fantasylol.schemas.search_parameters import GameSearchParameters


class GameServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()
        self.test_tournament = TournamentTestUtil.create_active_tournament()

    def create_game_service(self):
        return RiotGameService()

    def test_get_completed_games(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        GameTestUtil.create_unstarted_game(self.test_tournament.id)
        expected_game = GameTestUtil.create_completed_game(self.test_tournament.id)
        search_parameters = GameSearchParameters(state=GameState.COMPLETED)

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(search_parameters)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 1)
        self.assertEqual(games_from_db[0], expected_game)

    def test_get_completed_games_with_no_completed_games(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        GameTestUtil.create_unstarted_game(self.test_tournament.id)
        search_parameters = GameSearchParameters(state=GameState.COMPLETED)

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(search_parameters)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 0)

    def test_get_inprogress_games(self):
        GameTestUtil.create_unstarted_game(self.test_tournament.id)
        GameTestUtil.create_completed_game(self.test_tournament.id)
        expected_game = GameTestUtil.create_inprogress_game(self.test_tournament.id)
        search_parameters = GameSearchParameters(state=GameState.INPROGRESS)

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(search_parameters)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 1)
        self.assertEqual(games_from_db[0], expected_game)

    def test_get_inprogress_games_with_no_inprogress_games(self):
        GameTestUtil.create_completed_game(self.test_tournament.id)
        GameTestUtil.create_unstarted_game(self.test_tournament.id)
        search_parameters = GameSearchParameters(state=GameState.INPROGRESS)

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(search_parameters)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 0)

    def test_get_unstarted_games(self):
        GameTestUtil.create_completed_game(self.test_tournament.id)
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        expected_game = GameTestUtil.create_unstarted_game(self.test_tournament.id)
        search_parameters = GameSearchParameters(state=GameState.UNSTARTED)

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(search_parameters)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 1)
        self.assertEqual(games_from_db[0], expected_game)

    def test_get_unstarted_games_with_no_unstarted_games(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        GameTestUtil.create_completed_game(self.test_tournament.id)
        search_parameters = GameSearchParameters(state=GameState.UNSTARTED)

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(search_parameters)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 0)

    def test_get_games_by_match_id_existing_games(self):
        expected_game = GameTestUtil.create_inprogress_game(self.test_tournament.id)
        search_parameters = GameSearchParameters(match_id=expected_game.match_id)

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(search_parameters)
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(len(games_from_db), 1)
        self.assertEqual(games_from_db[0], expected_game)

    def test_get_games_by_match_id_no_existing_games(self):
        GameTestUtil.create_inprogress_game(self.test_tournament.id)
        search_parameters = GameSearchParameters(match_id=777)

        game_service = self.create_game_service()
        games_from_db = game_service.get_games(search_parameters)
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
