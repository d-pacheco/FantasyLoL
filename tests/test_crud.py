import copy

from fantasylol.db import crud
from fantasylol.schemas import riot_data_schemas as schemas
from fantasylol.db import models

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import db_util
from tests.test_util import test_fixtures
from tests.test_util import riot_data_util
from tests.test_util.game_stats_test_util import GameStatsTestUtil


class CrudTest(FantasyLolTestBase):
    # --------------------------------------------------
    # ----------- Player Metadata Operations -----------
    # --------------------------------------------------
    def test_get_games_without_player_metadata_completed_game_without_10_rows(self):
        game = riot_data_util.create_completed_game_in_db()
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_games_without_player_metadata_completed_game_with_10_rows(self):
        game = riot_data_util.create_completed_game_in_db()
        for participant_id in range(1, 11):
            GameStatsTestUtil.create_player_metadata(game.id, participant_id)
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_without_player_metadata_inprogress_game_without_10_rows(self):
        game = riot_data_util.create_inprogress_game_in_db()
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_games_without_player_metadata_inprogress_game_with_10_rows(self):
        game = riot_data_util.create_inprogress_game_in_db()
        for participant_id in range(1, 11):
            GameStatsTestUtil.create_player_metadata(game.id, participant_id)
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_without_player_metadata_unstarted_game_without_10_rows(self):
        riot_data_util.create_unstarted_game_in_db()
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    # --------------------------------------------------
    # ------------- Player Stats Operations ------------
    # --------------------------------------------------
    def test_get_game_ids_to_fetch_player_stats_for_completed_game_without_10_rows(self):
        game = riot_data_util.create_completed_game_in_db()
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_game_ids_to_fetch_player_stats_for_completed_game_with_10_rows(self):
        game = riot_data_util.create_completed_game_in_db()
        for participant_id in range(1, 11):
            GameStatsTestUtil.create_player_stats(game.id, participant_id)
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_game_ids_to_fetch_player_stats_for_inprogress_game_without_10_rows(self):
        game = riot_data_util.create_inprogress_game_in_db()
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_game_ids_to_fetch_player_stats_for_inprogress_game_with_10_rows(self):
        game = riot_data_util.create_inprogress_game_in_db()
        for participant_id in range(1, 11):
            GameStatsTestUtil.create_player_stats(game.id, participant_id)
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_game_ids_to_fetch_player_stats_for_unstarted_game_without_10_rows(self):
        riot_data_util.create_unstarted_game_in_db()
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    # --------------------------------------------------
    # ---------------- Game Operations -----------------
    # --------------------------------------------------
    def test_save_game(self):
        # Arrange
        game = test_fixtures.game_1_fixture_completed

        # Act
        crud.save_game(game)

        # Assert
        game_model_from_db = db_util.get_game(game.id)
        game_from_db = schemas.Game.model_validate(game_model_from_db)
        self.assertEqual(game, game_from_db)

    def test_bulk_save_games(self):
        # Arrange
        games_to_save = [
            test_fixtures.game_1_fixture_completed,
            test_fixtures.game_2_fixture_inprogress,
            test_fixtures.game_3_fixture_unstarted
        ]

        # Act
        crud.bulk_save_games(games_to_save)

        # Assert
        game_1_model_from_db = db_util.get_game(test_fixtures.game_1_fixture_completed.id)
        game_1_from_db = schemas.Game.model_validate(game_1_model_from_db)
        self.assertEqual(games_to_save[0], game_1_from_db)
        game_2_model_from_db = db_util.get_game(test_fixtures.game_2_fixture_inprogress.id)
        game_2_from_db = schemas.Game.model_validate(game_2_model_from_db)
        self.assertEqual(games_to_save[1], game_2_from_db)
        game_3_model_from_db = db_util.get_game(test_fixtures.game_3_fixture_unstarted.id)
        game_3_from_db = schemas.Game.model_validate(game_3_model_from_db)
        self.assertEqual(games_to_save[2], game_3_from_db)

    def test_get_games_no_filters(self):
        # Arrange
        expected_game = test_fixtures.game_1_fixture_completed
        db_util.save_game(expected_game)

        # Act
        game_models_from_db = crud.get_games()

        # Assert
        self.assertIsInstance(game_models_from_db, list)
        self.assertEqual(1, len(game_models_from_db))
        game_from_db = schemas.Game.model_validate(game_models_from_db[0])
        self.assertEqual(expected_game, game_from_db)

    def test_get_games_empty_filters(self):
        # Arrange
        filters = []
        expected_game = test_fixtures.game_1_fixture_completed
        db_util.save_game(expected_game)

        # Act
        game_models_from_db = crud.get_games(filters)

        # Assert
        self.assertIsInstance(game_models_from_db, list)
        self.assertEqual(1, len(game_models_from_db))
        game_from_db = schemas.Game.model_validate(game_models_from_db[0])
        self.assertEqual(expected_game, game_from_db)

    def test_get_games_game_state_filter(self):
        # Arrange
        filters = []
        expected_game = test_fixtures.game_1_fixture_completed
        filters.append(models.GameModel.state == expected_game.state)
        db_util.save_game(expected_game)
        db_util.save_game(test_fixtures.game_2_fixture_inprogress)
        db_util.save_game(test_fixtures.game_3_fixture_unstarted)

        # Act
        game_models_from_db = crud.get_games(filters)

        # Assert
        self.assertIsInstance(game_models_from_db, list)
        self.assertEqual(1, len(game_models_from_db))
        game_from_db = schemas.Game.model_validate(game_models_from_db[0])
        self.assertEqual(expected_game, game_from_db)

    def test_get_games_match_id_filter(self):
        # Arrange
        filters = []
        expected_game = test_fixtures.game_1_fixture_unstarted_future_match
        filters.append(models.GameModel.match_id == expected_game.match_id)
        db_util.save_game(expected_game)
        db_util.save_game(test_fixtures.game_3_fixture_unstarted)

        # Act
        game_models_from_db = crud.get_games(filters)

        # Assert
        self.assertIsInstance(game_models_from_db, list)
        self.assertEqual(1, len(game_models_from_db))
        game_from_db = schemas.Game.model_validate(game_models_from_db[0])
        self.assertEqual(expected_game, game_from_db)

    def test_get_game_by_id_existing_game(self):
        # Arrange
        expected_game = test_fixtures.game_1_fixture_completed
        db_util.save_game(expected_game)

        # Act
        game_model_from_db = crud.get_game_by_id(expected_game.id)

        # Assert
        game_from_db = schemas.Game.model_validate(game_model_from_db)
        self.assertEqual(expected_game, game_from_db)

    def test_get_game_by_id_no_existing_game(self):
        # Arrange
        expected_game = test_fixtures.game_1_fixture_completed

        # Act
        game_model_from_db = crud.get_game_by_id(expected_game.id)

        # Assert
        self.assertIsNone(game_model_from_db)

    def test_get_games_to_check_status_inprogress_game(self):
        # Arrange
        match_in_past = test_fixtures.match_fixture
        db_util.save_match(match_in_past)
        inprogress_game = test_fixtures.game_2_fixture_inprogress
        db_util.save_game(inprogress_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(inprogress_game.id, game_ids[0])

    def test_get_games_to_check_status_unstarted_game(self):
        # Arrange
        match_in_past = test_fixtures.match_fixture
        db_util.save_match(match_in_past)
        unstarted_game = test_fixtures.game_3_fixture_unstarted
        db_util.save_game(unstarted_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(unstarted_game.id, game_ids[0])

    def test_get_games_to_check_status_completed_game(self):
        # Arrange
        match_in_past = test_fixtures.match_fixture
        db_util.save_match(match_in_past)
        completed_game = test_fixtures.game_1_fixture_completed
        db_util.save_game(completed_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unneeded_game(self):
        # Arrange
        match_in_past = test_fixtures.match_fixture
        db_util.save_match(match_in_past)
        unneeded_game = test_fixtures.game_4_fixture_unneeded
        db_util.save_game(unneeded_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_inprogress_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = test_fixtures.future_match_fixture
        db_util.save_match(future_match)
        inprogress_game = test_fixtures.game_2_fixture_inprogress
        db_util.save_game(inprogress_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unstarted_game_future_match(self):
        # Arrange
        future_match = test_fixtures.future_match_fixture
        db_util.save_match(future_match)
        unstarted_game = test_fixtures.game_3_fixture_unstarted
        db_util.save_game(unstarted_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_completed_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = test_fixtures.future_match_fixture
        db_util.save_match(future_match)
        completed_game = test_fixtures.game_1_fixture_completed
        db_util.save_game(completed_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unneeded_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = test_fixtures.future_match_fixture
        db_util.save_match(future_match)
        unneeded_game = test_fixtures.game_4_fixture_unneeded
        db_util.save_game(unneeded_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_update_game_state(self):
        # Arrange
        unstarted_game = test_fixtures.game_3_fixture_unstarted
        db_util.save_game(unstarted_game)
        modified_game = copy.deepcopy(unstarted_game)
        modified_game.state = schemas.GameState.UNNEEDED

        # Act
        crud.update_game_state(unstarted_game.id, schemas.GameState.UNNEEDED.value)

        # Assert
        game_from_db = db_util.get_game(unstarted_game.id)
        self.assertEqual(modified_game.state, game_from_db.state)

    def test_update_has_game_data(self):
        # Arrange
        game = test_fixtures.game_4_fixture_unneeded
        db_util.save_game(game)
        modified_game = game
        modified_game.has_game_data = not game.has_game_data

        # Act
        crud.update_has_game_data(game.id, modified_game.has_game_data)

        # Assert
        game_from_db = db_util.get_game(game.id)
        self.assertEqual(modified_game.has_game_data, game_from_db.has_game_data)

    # --------------------------------------------------
    # --------------- League Operations ----------------
    # --------------------------------------------------
    def test_save_league(self):
        # Arrange
        expected_league = test_fixtures.league_1_fixture

        # Act
        crud.save_league(expected_league)

        # Assert
        league_model_from_db = db_util.get_league_by_id(expected_league.id)
        league_from_db = schemas.League.model_validate(league_model_from_db)
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_no_filters(self):
        # Arrange
        expected_league = test_fixtures.league_1_fixture
        db_util.save_league(expected_league)

        # Act
        league_models_from_db = crud.get_leagues()

        # Assert
        self.assertIsInstance(league_models_from_db, list)
        self.assertEqual(1, len(league_models_from_db))
        league_from_db = schemas.League.model_validate(league_models_from_db[0])
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_empty_filters(self):
        # Arrange
        filters = []
        expected_league = test_fixtures.league_1_fixture
        db_util.save_league(expected_league)

        # Act
        league_models_from_db = crud.get_leagues(filters)

        # Assert
        self.assertIsInstance(league_models_from_db, list)
        self.assertEqual(1, len(league_models_from_db))
        league_from_db = schemas.League.model_validate(league_models_from_db[0])
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_name_filter(self):
        # Arrange
        filters = []
        expected_league = test_fixtures.league_1_fixture
        filters.append(models.LeagueModel.name == expected_league.name)
        db_util.save_league(expected_league)
        db_util.save_league(test_fixtures.league_2_fixture)

        # Act
        league_models_from_db = crud.get_leagues(filters)

        # Assert
        self.assertIsInstance(league_models_from_db, list)
        self.assertEqual(1, len(league_models_from_db))
        league_from_db = schemas.League.model_validate(league_models_from_db[0])
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_name_filter_no_league(self):
        # Arrange
        filters = []
        expected_league = test_fixtures.league_1_fixture
        filters.append(models.LeagueModel.name == expected_league.name)
        db_util.save_league(test_fixtures.league_2_fixture)

        # Act
        league_models_from_db = crud.get_leagues(filters)

        # Assert
        self.assertIsInstance(league_models_from_db, list)
        self.assertEqual(0, len(league_models_from_db))

    def test_get_leagues_region_filter(self):
        # Arrange
        filters = []
        expected_league = test_fixtures.league_1_fixture
        filters.append(models.LeagueModel.region == expected_league.region)
        db_util.save_league(expected_league)
        db_util.save_league(test_fixtures.league_2_fixture)

        # Act
        league_models_from_db = crud.get_leagues(filters)

        # Assert
        self.assertIsInstance(league_models_from_db, list)
        self.assertEqual(1, len(league_models_from_db))
        league_from_db = schemas.League.model_validate(league_models_from_db[0])
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_region_filter_no_league(self):
        # Arrange
        filters = []
        expected_league = test_fixtures.league_1_fixture
        filters.append(models.LeagueModel.region == expected_league.region)
        db_util.save_league(test_fixtures.league_2_fixture)

        # Act
        league_models_from_db = crud.get_leagues(filters)

        # Assert
        self.assertIsInstance(league_models_from_db, list)
        self.assertEqual(0, len(league_models_from_db))

    def test_get_league_by_id_existing_league(self):
        # Arrange
        expected_league = test_fixtures.league_1_fixture
        db_util.save_league(expected_league)

        # Act
        league_model_from_db = crud.get_league_by_id(expected_league.id)

        # Assert
        self.assertIsNotNone(league_model_from_db)
        league_from_db = schemas.League.model_validate(league_model_from_db)
        self.assertEqual(expected_league, league_from_db)

    def test_get_league_by_id_no_existing_league(self):
        # Arrange
        expected_league = test_fixtures.league_1_fixture

        # Act
        league_model_from_db = crud.get_league_by_id(expected_league.id)

        # Assert
        self.assertIsNone(league_model_from_db)
