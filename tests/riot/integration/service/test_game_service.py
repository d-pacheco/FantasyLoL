from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.schemas.riot_data_schemas import GameState, RiotGameID
from src.common.schemas.search_parameters import GameSearchParameters
from src.riot.exceptions import GameNotFoundException
from src.riot.service import RiotGameService



class GameServiceTest(TestBase):
    def setUp(self):
        super().setUp()
        self.game_service = RiotGameService(self.db)

    def test_get_completed_games(self):
        # Arrange
        expected_game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(riot_fixtures.game_4_fixture_unneeded)
        self.db.put_game(riot_fixtures.game_2_fixture_inprogress)
        self.db.put_game(riot_fixtures.game_3_fixture_unstarted)
        self.db.put_game(expected_game)
        search_parameters = GameSearchParameters(state=GameState.COMPLETED)

        # Act
        games_from_db = self.game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        self.assertEqual(expected_game, games_from_db[0])

    def test_get_completed_games_with_no_completed_games_in_db(self):
        # Arrange
        self.db.put_game(riot_fixtures.game_4_fixture_unneeded)
        self.db.put_game(riot_fixtures.game_2_fixture_inprogress)
        self.db.put_game(riot_fixtures.game_3_fixture_unstarted)
        search_parameters = GameSearchParameters(state=GameState.COMPLETED)

        # Act
        games_from_db = self.game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(0, len(games_from_db))

    def test_get_inprogress_games(self):
        # Arrange
        expected_game = riot_fixtures.game_2_fixture_inprogress
        self.db.put_game(riot_fixtures.game_4_fixture_unneeded)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)
        self.db.put_game(riot_fixtures.game_3_fixture_unstarted)
        self.db.put_game(expected_game)
        search_parameters = GameSearchParameters(state=GameState.INPROGRESS)

        # Act
        games_from_db = self.game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        self.assertEqual(expected_game, games_from_db[0])

    def test_get_inprogress_games_with_no_inprogress_games_in_db(self):
        # Arrange
        self.db.put_game(riot_fixtures.game_4_fixture_unneeded)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)
        self.db.put_game(riot_fixtures.game_3_fixture_unstarted)
        search_parameters = GameSearchParameters(state=GameState.INPROGRESS)

        # Act
        games_from_db = self.game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(0, len(games_from_db))

    def test_get_unstarted_games(self):
        # Arrange
        expected_game = riot_fixtures.game_3_fixture_unstarted
        self.db.put_game(riot_fixtures.game_4_fixture_unneeded)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)
        self.db.put_game(riot_fixtures.game_2_fixture_inprogress)
        self.db.put_game(expected_game)
        search_parameters = GameSearchParameters(state=GameState.UNSTARTED)

        # Act
        games_from_db = self.game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        self.assertEqual(expected_game, games_from_db[0])

    def test_get_unstarted_games_with_no_unstarted_games_in_db(self):
        # Arrange
        self.db.put_game(riot_fixtures.game_4_fixture_unneeded)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)
        self.db.put_game(riot_fixtures.game_2_fixture_inprogress)
        search_parameters = GameSearchParameters(state=GameState.UNSTARTED)

        # Act
        games_from_db = self.game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(0, len(games_from_db))

    def test_get_unneeded_games(self):
        # Arrange
        expected_game = riot_fixtures.game_4_fixture_unneeded
        self.db.put_game(riot_fixtures.game_3_fixture_unstarted)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)
        self.db.put_game(riot_fixtures.game_2_fixture_inprogress)
        self.db.put_game(expected_game)
        search_parameters = GameSearchParameters(state=GameState.UNNEEDED)

        # Act
        games_from_db = self.game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        self.assertEqual(expected_game, games_from_db[0])

    def test_get_unneeded_games_with_no_unneeded_games_in_db(self):
        # Arrange
        self.db.put_game(riot_fixtures.game_1_fixture_completed)
        self.db.put_game(riot_fixtures.game_2_fixture_inprogress)
        self.db.put_game(riot_fixtures.game_3_fixture_unstarted)
        search_parameters = GameSearchParameters(state=GameState.UNNEEDED)

        # Act
        games_from_db = self.game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(0, len(games_from_db))

    def test_get_games_by_match_id_existing_games(self):
        # Arrange
        expected_game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(expected_game)
        search_parameters = GameSearchParameters(match_id=expected_game.match_id)

        # Act
        games_from_db = self.game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        self.assertEqual(expected_game, games_from_db[0])

    def test_get_games_by_match_id_no_existing_games(self):
        # Arrange
        self.db.put_game(riot_fixtures.game_1_fixture_completed)
        search_parameters = GameSearchParameters(match_id="777")

        # Act
        games_from_db = self.game_service.get_games(search_parameters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(0, len(games_from_db))

    def test_get_game_by_id_valid_id(self):
        # Arrange
        expected_game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(expected_game)

        # Act
        game_from_db = self.game_service.get_game_by_id(expected_game.id)

        # Assert
        self.assertEqual(expected_game, game_from_db)

    def test_get_game_by_id_invalid_id(self):
        # Arrange
        self.db.put_game(riot_fixtures.game_1_fixture_completed)

        # Act and Assert
        with self.assertRaises(GameNotFoundException):
            self.game_service.get_game_by_id(RiotGameID("777"))
