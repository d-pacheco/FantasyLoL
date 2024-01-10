from fantasylol.db import crud

from tests.fantasy_lol_test_base import FantasyLolTestBase
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
