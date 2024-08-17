from src.common.schemas.riot_data_schemas import Game, GameState
from src.db.models import GameModel
from tests.test_base import TestBase
from tests.test_util import riot_fixtures


class TestCrudRiotGame(TestBase):
    def test_put_game_no_existing_game(self):
        # Arrange
        game = riot_fixtures.game_1_fixture_completed

        # Act and Assert
        game_before_put = self.db.get_game_by_id(game.id)
        self.assertIsNone(game_before_put)
        self.db.put_game(game)
        game_after_put = self.db.get_game_by_id(game.id)
        self.assertEqual(game, game_after_put)

    def test_put_game_existing_game(self):
        # Arrange
        game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(game)
        updated_game = game.model_copy(deep=True)
        updated_game.has_game_data = not game.has_game_data

        # Act and Assert
        game_before_put = self.db.get_game_by_id(game.id)
        self.assertEqual(game, game_before_put)
        self.assertEqual(game.id, updated_game.id)
        self.db.put_game(updated_game)
        game_after_put = self.db.get_game_by_id(game.id)
        self.assertEqual(updated_game, game_after_put)

    def test_bulk_save_games(self):
        # Arrange
        games_to_save = [
            riot_fixtures.game_1_fixture_completed,
            riot_fixtures.game_2_fixture_inprogress,
            riot_fixtures.game_3_fixture_unstarted
        ]

        # Act
        self.db.bulk_save_games(games_to_save)

        # Assert
        game_1_from_db = self.db.get_game_by_id(riot_fixtures.game_1_fixture_completed.id)
        self.assertEqual(games_to_save[0], game_1_from_db)
        game_2_from_db = self.db.get_game_by_id(riot_fixtures.game_2_fixture_inprogress.id)
        self.assertEqual(games_to_save[1], game_2_from_db)
        game_3_from_db = self.db.get_game_by_id(riot_fixtures.game_3_fixture_unstarted.id)
        self.assertEqual(games_to_save[2], game_3_from_db)

    def test_get_games_no_filters(self):
        # Arrange
        expected_game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(expected_game)

        # Act
        games_from_db = self.db.get_games()

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        game_from_db = games_from_db[0]
        self.assertIsInstance(game_from_db, Game)
        self.assertEqual(expected_game, game_from_db)

    def test_get_games_empty_filters(self):
        # Arrange
        filters = []
        expected_game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(expected_game)

        # Act
        games_from_db = self.db.get_games(filters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        game_from_db = games_from_db[0]
        self.assertIsInstance(game_from_db, Game)
        self.assertEqual(expected_game, game_from_db)

    def test_get_games_game_state_filter(self):
        # Arrange
        filters = []
        expected_game = riot_fixtures.game_1_fixture_completed
        filters.append(GameModel.state == expected_game.state)
        self.db.put_game(expected_game)
        self.db.put_game(riot_fixtures.game_2_fixture_inprogress)
        self.db.put_game(riot_fixtures.game_3_fixture_unstarted)

        # Act
        games_from_db = self.db.get_games(filters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        game_from_db = games_from_db[0]
        self.assertIsInstance(game_from_db, Game)
        self.assertEqual(expected_game, game_from_db)

    def test_get_games_match_id_filter(self):
        # Arrange
        filters = []
        expected_game = riot_fixtures.game_1_fixture_unstarted_future_match
        filters.append(GameModel.match_id == expected_game.match_id)
        self.db.put_game(expected_game)
        self.db.put_game(riot_fixtures.game_3_fixture_unstarted)

        # Act
        games_from_db = self.db.get_games(filters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        game_from_db = games_from_db[0]
        self.assertIsInstance(game_from_db, Game)
        self.assertEqual(expected_game, game_from_db)

    def test_get_game_by_id_existing_game(self):
        # Arrange
        expected_game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(expected_game)

        # Act
        game_from_db = self.db.get_game_by_id(expected_game.id)

        # Assert
        self.assertIsInstance(game_from_db, Game)
        self.assertEqual(expected_game, game_from_db)

    def test_get_game_by_id_no_existing_game(self):
        # Arrange
        expected_game = riot_fixtures.game_1_fixture_completed

        # Act
        game_from_db = self.db.get_game_by_id(expected_game.id)

        # Assert
        self.assertIsNone(game_from_db)

    def test_get_games_to_check_status_inprogress_game(self):
        # Arrange
        match_in_past = riot_fixtures.match_fixture
        self.db.put_match(match_in_past)
        inprogress_game = riot_fixtures.game_2_fixture_inprogress
        self.db.put_game(inprogress_game)

        # Act
        game_ids = self.db.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(inprogress_game.id, game_ids[0])

    def test_get_games_to_check_status_unstarted_game(self):
        # Arrange
        match_in_past = riot_fixtures.match_fixture
        self.db.put_match(match_in_past)
        unstarted_game = riot_fixtures.game_3_fixture_unstarted
        self.db.put_game(unstarted_game)

        # Act
        game_ids = self.db.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(unstarted_game.id, game_ids[0])

    def test_get_games_to_check_status_completed_game(self):
        # Arrange
        match_in_past = riot_fixtures.match_fixture
        self.db.put_match(match_in_past)
        completed_game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(completed_game)

        # Act
        game_ids = self.db.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unneeded_game(self):
        # Arrange
        match_in_past = riot_fixtures.match_fixture
        self.db.put_match(match_in_past)
        unneeded_game = riot_fixtures.game_4_fixture_unneeded
        self.db.put_game(unneeded_game)

        # Act
        game_ids = self.db.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_inprogress_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = riot_fixtures.future_match_fixture
        self.db.put_match(future_match)
        inprogress_game = riot_fixtures.game_2_fixture_inprogress
        self.db.put_game(inprogress_game)

        # Act
        game_ids = self.db.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unstarted_game_future_match(self):
        # Arrange
        future_match = riot_fixtures.future_match_fixture
        self.db.put_match(future_match)
        unstarted_game = riot_fixtures.game_3_fixture_unstarted
        self.db.put_game(unstarted_game)

        # Act
        game_ids = self.db.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_completed_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = riot_fixtures.future_match_fixture
        self.db.put_match(future_match)
        completed_game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(completed_game)

        # Act
        game_ids = self.db.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unneeded_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = riot_fixtures.future_match_fixture
        self.db.put_match(future_match)
        unneeded_game = riot_fixtures.game_4_fixture_unneeded
        self.db.put_game(unneeded_game)

        # Act
        game_ids = self.db.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_update_game_state(self):
        # Arrange
        unstarted_game = riot_fixtures.game_3_fixture_unstarted
        self.db.put_game(unstarted_game)
        modified_game = unstarted_game.model_copy(deep=True)
        modified_game.state = GameState.UNNEEDED

        # Act
        self.db.update_game_state(unstarted_game.id, GameState.UNNEEDED.value)

        # Assert
        game_from_db = self.db.get_game_by_id(unstarted_game.id)
        self.assertEqual(modified_game.state, game_from_db.state)

    def test_update_has_game_data(self):
        # Arrange
        game = riot_fixtures.game_4_fixture_unneeded
        self.db.put_game(game)
        modified_game = game
        modified_game.has_game_data = not game.has_game_data

        # Act
        self.db.update_has_game_data(game.id, modified_game.has_game_data)

        # Assert
        game_from_db = self.db.get_game_by_id(game.id)
        self.assertEqual(modified_game.has_game_data, game_from_db.has_game_data)
