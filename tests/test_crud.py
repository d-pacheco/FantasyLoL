from fantasylol.db import crud
from fantasylol.schemas.game_state import GameState

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import db_util
from tests.test_util.test_fixtures import TestFixtures
from tests.test_util.game_test_util import GameTestUtil
from tests.test_util.game_stats_test_util import GameStatsTestUtil


class CrudTest(FantasyLolTestBase):
    # --------------------------------------------------
    # ----------- Player Metadata Operations -----------
    # --------------------------------------------------
    def test_get_games_without_player_metadata_completed_game_without_10_rows(self):
        game = GameTestUtil.create_completed_game()
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_games_without_player_metadata_completed_game_with_10_rows(self):
        game = GameTestUtil.create_completed_game()
        for participant_id in range(1, 11):
            GameStatsTestUtil.create_player_metadata(game.id, participant_id)
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_without_player_metadata_inprogress_game_without_10_rows(self):
        game = GameTestUtil.create_inprogress_game()
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_games_without_player_metadata_inprogress_game_with_10_rows(self):
        game = GameTestUtil.create_inprogress_game()
        for participant_id in range(1, 11):
            GameStatsTestUtil.create_player_metadata(game.id, participant_id)
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_without_player_metadata_unstarted_game_without_10_rows(self):
        GameTestUtil.create_unstarted_game()
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    # --------------------------------------------------
    # ------------- Player Stats Operations ------------
    # --------------------------------------------------
    def test_get_game_ids_to_fetch_player_stats_for_completed_game_without_10_rows(self):
        game = GameTestUtil.create_completed_game()
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_game_ids_to_fetch_player_stats_for_completed_game_with_10_rows(self):
        game = GameTestUtil.create_completed_game()
        for participant_id in range(1, 11):
            GameStatsTestUtil.create_player_stats(game.id, participant_id)
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_game_ids_to_fetch_player_stats_for_inprogress_game_without_10_rows(self):
        game = GameTestUtil.create_inprogress_game()
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_game_ids_to_fetch_player_stats_for_inprogress_game_with_10_rows(self):
        game = GameTestUtil.create_inprogress_game()
        for participant_id in range(1, 11):
            GameStatsTestUtil.create_player_stats(game.id, participant_id)
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_game_ids_to_fetch_player_stats_for_unstarted_game_without_10_rows(self):
        GameTestUtil.create_unstarted_game()
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    # --------------------------------------------------
    # ---------------- Game Operations -----------------
    # --------------------------------------------------
    def test_get_games_to_check_status_inprogress_game(self):
        # Arrange
        match_in_past = TestFixtures.match_fixture
        db_util.save_match(match_in_past)
        inprogress_game = TestFixtures.game_2_fixture_inprogress
        db_util.save_game(inprogress_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(inprogress_game.id, game_ids[0])

    def test_get_games_to_check_status_unstarted_game(self):
        # Arrange
        match_in_past = TestFixtures.match_fixture
        db_util.save_match(match_in_past)
        unstarted_game = TestFixtures.game_3_fixture_unstarted
        db_util.save_game(unstarted_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(unstarted_game.id, game_ids[0])

    def test_get_games_to_check_status_completed_game(self):
        # Arrange
        match_in_past = TestFixtures.match_fixture
        db_util.save_match(match_in_past)
        completed_game = TestFixtures.game_1_fixture_completed
        db_util.save_game(completed_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unneeded_game(self):
        # Arrange
        match_in_past = TestFixtures.match_fixture
        db_util.save_match(match_in_past)
        unneeded_game = TestFixtures.game_4_fixture_unneeded
        db_util.save_game(unneeded_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_inprogress_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = TestFixtures.future_match_fixture
        db_util.save_match(future_match)
        inprogress_game = TestFixtures.game_2_fixture_inprogress
        db_util.save_game(inprogress_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unstarted_game_future_match(self):
        # Arrange
        future_match = TestFixtures.future_match_fixture
        db_util.save_match(future_match)
        unstarted_game = TestFixtures.game_3_fixture_unstarted
        db_util.save_game(unstarted_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_completed_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = TestFixtures.future_match_fixture
        db_util.save_match(future_match)
        completed_game = TestFixtures.game_1_fixture_completed
        db_util.save_game(completed_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unneeded_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = TestFixtures.future_match_fixture
        db_util.save_match(future_match)
        unneeded_game = TestFixtures.game_4_fixture_unneeded
        db_util.save_game(unneeded_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_update_game_state(self):
        # Arrange
        unstarted_game = TestFixtures.game_3_fixture_unstarted
        db_util.save_game(unstarted_game)
        modified_game = unstarted_game
        modified_game.state = GameState.UNNEEDED

        # Act
        crud.update_game_state(unstarted_game.id, GameState.UNNEEDED.value)

        # Assert
        game_from_db = db_util.get_game(unstarted_game.id)
        self.assertEqual(modified_game.state, game_from_db.state)

    def test_update_has_game_data(self):
        # Arrange
        game = TestFixtures.game_4_fixture_unneeded
        db_util.save_game(game)
        modified_game = game
        modified_game.has_game_data = not game.has_game_data

        # Act
        crud.update_has_game_data(game.id, modified_game.has_game_data)

        # Assert
        game_from_db = db_util.get_game(game.id)
        self.assertEqual(modified_game.has_game_data, game_from_db.has_game_data)
