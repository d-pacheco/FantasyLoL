from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import riot_data_util

from riot.exceptions.game_not_found_exception import GameNotFoundException
from riot.service.riot_game_service import RiotGameService
from common.schemas.riot_data_schemas import GameState
from common.schemas.search_parameters import GameSearchParameters


def create_game_service():
    return RiotGameService()


class GameServiceTest(FantasyLolTestBase):
    def test_get_completed_games(self):
        # Arrange
        game_service = create_game_service()
        riot_data_util.create_unneeded_game_in_db()
        riot_data_util.create_inprogress_game_in_db()
        riot_data_util.create_unstarted_game_in_db()
        expected_game = riot_data_util.create_completed_game_in_db()
        search_parameters = GameSearchParameters(state=GameState.COMPLETED)

        # Act
        games_from_db = game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        self.assertEqual(expected_game, games_from_db[0])

    def test_get_completed_games_with_no_completed_games_in_db(self):
        # Arrange
        game_service = create_game_service()
        riot_data_util.create_unneeded_game_in_db()
        riot_data_util.create_inprogress_game_in_db()
        riot_data_util.create_unstarted_game_in_db()
        search_parameters = GameSearchParameters(state=GameState.COMPLETED)

        # Act
        games_from_db = game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(0, len(games_from_db))

    def test_get_inprogress_games(self):
        # Arrange
        game_service = create_game_service()
        riot_data_util.create_unneeded_game_in_db()
        riot_data_util.create_completed_game_in_db()
        riot_data_util.create_unstarted_game_in_db()
        expected_game = riot_data_util.create_inprogress_game_in_db()
        search_parameters = GameSearchParameters(state=GameState.INPROGRESS)

        # Act
        games_from_db = game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        self.assertEqual(expected_game, games_from_db[0])

    def test_get_inprogress_games_with_no_inprogress_games_in_db(self):
        # Arrange
        game_service = create_game_service()
        riot_data_util.create_unneeded_game_in_db()
        riot_data_util.create_completed_game_in_db()
        riot_data_util.create_unstarted_game_in_db()
        search_parameters = GameSearchParameters(state=GameState.INPROGRESS)

        # Act
        games_from_db = game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(0, len(games_from_db))

    def test_get_unstarted_games(self):
        # Arrange
        game_service = create_game_service()
        riot_data_util.create_unneeded_game_in_db()
        riot_data_util.create_completed_game_in_db()
        riot_data_util.create_inprogress_game_in_db()
        expected_game = riot_data_util.create_unstarted_game_in_db()
        search_parameters = GameSearchParameters(state=GameState.UNSTARTED)

        # Act
        games_from_db = game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        self.assertEqual(expected_game, games_from_db[0])

    def test_get_unstarted_games_with_no_unstarted_games_in_db(self):
        # Arrange
        game_service = create_game_service()
        riot_data_util.create_unneeded_game_in_db()
        riot_data_util.create_completed_game_in_db()
        riot_data_util.create_inprogress_game_in_db()
        search_parameters = GameSearchParameters(state=GameState.UNSTARTED)

        # Act
        games_from_db = game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(0, len(games_from_db))

    def test_get_unneeded_games(self):
        # Arrange
        game_service = create_game_service()
        riot_data_util.create_unstarted_game_in_db()
        riot_data_util.create_completed_game_in_db()
        riot_data_util.create_inprogress_game_in_db()
        expected_game = riot_data_util.create_unneeded_game_in_db()
        search_parameters = GameSearchParameters(state=GameState.UNNEEDED)

        # Act
        games_from_db = game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        self.assertEqual(expected_game, games_from_db[0])

    def test_get_unneeded_games_with_no_unneeded_games_in_db(self):
        # Arrange
        game_service = create_game_service()
        riot_data_util.create_completed_game_in_db()
        riot_data_util.create_inprogress_game_in_db()
        riot_data_util.create_unstarted_game_in_db()
        search_parameters = GameSearchParameters(state=GameState.UNNEEDED)

        # Act
        games_from_db = game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(0, len(games_from_db))

    def test_get_games_by_match_id_existing_games(self):
        # Arrange
        expected_game = riot_data_util.create_completed_game_in_db()
        search_parameters = GameSearchParameters(match_id=expected_game.match_id)
        game_service = create_game_service()

        # Act
        games_from_db = game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        self.assertEqual(expected_game, games_from_db[0])

    def test_get_games_by_match_id_no_existing_games(self):
        # Arrange
        riot_data_util.create_completed_game_in_db()
        search_parameters = GameSearchParameters(match_id="777")
        game_service = create_game_service()

        # Act
        games_from_db = game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(0, len(games_from_db))

    def test_get_game_by_id_valid_id(self):
        # Arrange
        expected_game = riot_data_util.create_completed_game_in_db()
        game_service = create_game_service()

        # Act
        game_from_db = game_service.get_game_by_id(expected_game.id)

        # Assert
        self.assertEqual(expected_game, game_from_db)

    def test_get_game_by_id_invalid_id(self):
        # Arrange
        riot_data_util.create_completed_game_in_db()
        game_service = create_game_service()

        # Act and Assert
        with self.assertRaises(GameNotFoundException):
            game_service.get_game_by_id("777")
