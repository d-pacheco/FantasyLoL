from sqlalchemy.exc import IntegrityError
import copy
from datetime import datetime

from src.db import views
from src.db import models, crud
from src.common.schemas.riot_data_schemas import *
from src.common.schemas.fantasy_schemas import *
from src.common.schemas import fantasy_schemas, riot_data_schemas as schemas

from tests.test_base import FantasyLolTestBase
from tests.test_util import db_util, riot_fixtures, riot_data_util, fantasy_fixtures
from tests.test_util.game_stats_test_util import GameStatsTestUtil


class CrudTest(FantasyLolTestBase):
    # --------------------------------------------------
    # --------------- Player Operations ----------------
    # --------------------------------------------------
    def test_save_player(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture

        # Act
        crud.save_player(expected_player)

        # Assert
        player_model_from_db = db_util.get_player_by_id(expected_player.id)
        self.assertIsNotNone(player_model_from_db)
        player_from_db = schemas.ProfessionalPlayer.model_validate(player_model_from_db)
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_no_filters(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        db_util.save_player(expected_player)

        # Act
        player_models_from_db = crud.get_players()

        # Assert
        self.assertIsInstance(player_models_from_db, list)
        self.assertEqual(1, len(player_models_from_db))
        player_from_db = schemas.ProfessionalPlayer.model_validate(player_models_from_db[0])
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_empty_filters(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        db_util.save_player(expected_player)

        # Act
        player_models_from_db = crud.get_players(filters)

        # Assert
        self.assertIsInstance(player_models_from_db, list)
        self.assertEqual(1, len(player_models_from_db))
        player_from_db = schemas.ProfessionalPlayer.model_validate(player_models_from_db[0])
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_summoner_name_filter_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_6_fixture
        filters.append(
            models.ProfessionalPlayerModel.summoner_name == expected_player.summoner_name
        )
        db_util.save_player(expected_player)
        db_util.save_player(other_player)

        # Act
        player_models_from_db = crud.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player, other_player)
        self.assertIsInstance(player_models_from_db, list)
        self.assertEqual(1, len(player_models_from_db))
        player_from_db = schemas.ProfessionalPlayer.model_validate(player_models_from_db[0])
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_summoner_name_filter_no_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_6_fixture
        filters.append(
            models.ProfessionalPlayerModel.summoner_name == expected_player.summoner_name
        )
        db_util.save_player(other_player)

        # Act
        player_models_from_db = crud.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player.summoner_name, other_player.summoner_name)
        self.assertIsInstance(player_models_from_db, list)
        self.assertEqual(0, len(player_models_from_db))

    def test_get_players_team_id_filter_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_6_fixture
        filters.append(models.ProfessionalPlayerModel.team_id == expected_player.team_id)
        db_util.save_player(expected_player)
        db_util.save_player(other_player)

        # Act
        player_models_from_db = crud.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player, other_player)
        self.assertIsInstance(player_models_from_db, list)
        self.assertEqual(1, len(player_models_from_db))
        player_from_db = schemas.ProfessionalPlayer.model_validate(player_models_from_db[0])
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_team_id_filter_no_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_6_fixture
        filters.append(models.ProfessionalPlayerModel.team_id == expected_player.team_id)
        db_util.save_player(other_player)

        # Act
        player_models_from_db = crud.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player.team_id, other_player.team_id)
        self.assertIsInstance(player_models_from_db, list)
        self.assertEqual(0, len(player_models_from_db))

    def test_get_players_role_filter_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_7_fixture
        filters.append(models.ProfessionalPlayerModel.role == expected_player.role)
        db_util.save_player(expected_player)
        db_util.save_player(other_player)

        # Act
        player_models_from_db = crud.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player, other_player)
        self.assertIsInstance(player_models_from_db, list)
        self.assertEqual(1, len(player_models_from_db))
        player_from_db = schemas.ProfessionalPlayer.model_validate(player_models_from_db[0])
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_role_filter_no_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_7_fixture
        filters.append(models.ProfessionalPlayerModel.role == expected_player.role)
        db_util.save_player(other_player)

        # Act
        player_models_from_db = crud.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player.role, other_player.role)
        self.assertIsInstance(player_models_from_db, list)
        self.assertEqual(0, len(player_models_from_db))

    def test_get_player_by_id_existing_player(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        db_util.save_player(expected_player)

        # Act
        player_model_from_db = crud.get_player_by_id(expected_player.id)

        # Assert
        self.assertIsNotNone(player_model_from_db)
        player_from_db = schemas.ProfessionalPlayer.model_validate(player_model_from_db)
        self.assertEqual(expected_player, player_from_db)

    def test_get_player_by_id_no_existing_player(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture

        # Act
        player_model_from_db = crud.get_player_by_id(expected_player.id)

        # Assert
        self.assertIsNone(player_model_from_db)

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

    def test_get_player_game_stats_no_filters(self):
        # Arrange
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        db_util.save_player_metadata(riot_fixtures.player_1_game_metadata_fixture)
        db_util.save_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        player_game_data_models_from_db = crud.get_player_game_stats()

        # Assert
        self.assertIsInstance(player_game_data_models_from_db, list)
        self.assertEqual(1, len(player_game_data_models_from_db))
        player_game_data_from_db = schemas.PlayerGameData.model_validate(
            player_game_data_models_from_db[0]
        )
        self.assertEqual(expected_player_game_data, player_game_data_from_db)

    def test_get_player_game_stats_empty_filter(self):
        # Arrange
        filters = []
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        db_util.save_player_metadata(riot_fixtures.player_1_game_metadata_fixture)
        db_util.save_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        player_game_data_models_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(player_game_data_models_from_db, list)
        self.assertEqual(1, len(player_game_data_models_from_db))
        player_game_data_from_db = schemas.PlayerGameData.model_validate(
            player_game_data_models_from_db[0]
        )
        self.assertEqual(expected_player_game_data, player_game_data_from_db)

    def test_get_player_game_stats_has_metadata_but_no_stats(self):
        # Arrange
        filters = []
        db_util.save_player_metadata(riot_fixtures.player_1_game_metadata_fixture)

        # Act
        player_game_data_models_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(player_game_data_models_from_db, list)
        self.assertEqual(0, len(player_game_data_models_from_db))

    def test_get_player_game_stats_has_stats_but_no_metadata(self):
        # Arrange
        filters = []
        db_util.save_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        player_game_data_models_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(player_game_data_models_from_db, list)
        self.assertEqual(0, len(player_game_data_models_from_db))

    def test_get_player_game_stats_game_id_filter_existing_stats(self):
        # Arrange
        filters = []
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        filters.append(views.PlayerGameView.game_id == expected_player_game_data.game_id)
        db_util.save_player_metadata(riot_fixtures.player_1_game_metadata_fixture)
        db_util.save_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        player_game_data_models_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(player_game_data_models_from_db, list)
        self.assertEqual(1, len(player_game_data_models_from_db))
        player_game_data_from_db = schemas.PlayerGameData.model_validate(
            player_game_data_models_from_db[0]
        )
        self.assertEqual(expected_player_game_data, player_game_data_from_db)

    def test_get_player_game_stats_game_id_filter_no_existing_stats(self):
        # Arrange
        filters = []
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        filters.append(views.PlayerGameView.game_id == expected_player_game_data.game_id)

        # Act
        player_game_data_models_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(player_game_data_models_from_db, list)
        self.assertEqual(0, len(player_game_data_models_from_db))

    def test_get_player_game_stats_player_id_filter_existing_stats(self):
        # Arrange
        filters = []
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        filters.append(views.PlayerGameView.player_id == expected_player_game_data.player_id)
        db_util.save_player_metadata(riot_fixtures.player_1_game_metadata_fixture)
        db_util.save_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        player_game_data_models_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(player_game_data_models_from_db, list)
        self.assertEqual(1, len(player_game_data_models_from_db))
        player_game_data_from_db = schemas.PlayerGameData.model_validate(
            player_game_data_models_from_db[0]
        )
        self.assertEqual(expected_player_game_data, player_game_data_from_db)

    def test_get_player_game_stats_player_id_filter_no_existing_stats(self):
        # Arrange
        filters = []
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        filters.append(views.PlayerGameView.player_id == expected_player_game_data.player_id)
        db_util.save_player_metadata(riot_fixtures.player_1_game_metadata_fixture)
        db_util.save_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        player_game_data_models_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(player_game_data_models_from_db, list)
        self.assertEqual(1, len(player_game_data_models_from_db))
        player_game_data_from_db = schemas.PlayerGameData.model_validate(
            player_game_data_models_from_db[0]
        )
        self.assertEqual(expected_player_game_data, player_game_data_from_db)

    # --------------------------------------------------
    # ---------------- Game Operations -----------------
    # --------------------------------------------------
    def test_save_game(self):
        # Arrange
        game = riot_fixtures.game_1_fixture_completed

        # Act
        crud.save_game(game)

        # Assert
        game_model_from_db = db_util.get_game(game.id)
        game_from_db = schemas.Game.model_validate(game_model_from_db)
        self.assertEqual(game, game_from_db)

    def test_bulk_save_games(self):
        # Arrange
        games_to_save = [
            riot_fixtures.game_1_fixture_completed,
            riot_fixtures.game_2_fixture_inprogress,
            riot_fixtures.game_3_fixture_unstarted
        ]

        # Act
        crud.bulk_save_games(games_to_save)

        # Assert
        game_1_model_from_db = db_util.get_game(riot_fixtures.game_1_fixture_completed.id)
        game_1_from_db = schemas.Game.model_validate(game_1_model_from_db)
        self.assertEqual(games_to_save[0], game_1_from_db)
        game_2_model_from_db = db_util.get_game(riot_fixtures.game_2_fixture_inprogress.id)
        game_2_from_db = schemas.Game.model_validate(game_2_model_from_db)
        self.assertEqual(games_to_save[1], game_2_from_db)
        game_3_model_from_db = db_util.get_game(riot_fixtures.game_3_fixture_unstarted.id)
        game_3_from_db = schemas.Game.model_validate(game_3_model_from_db)
        self.assertEqual(games_to_save[2], game_3_from_db)

    def test_get_games_no_filters(self):
        # Arrange
        expected_game = riot_fixtures.game_1_fixture_completed
        db_util.save_game(expected_game)

        # Act
        games_from_db = crud.get_games()

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
        db_util.save_game(expected_game)

        # Act
        games_from_db = crud.get_games(filters)

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
        filters.append(models.GameModel.state == expected_game.state)
        db_util.save_game(expected_game)
        db_util.save_game(riot_fixtures.game_2_fixture_inprogress)
        db_util.save_game(riot_fixtures.game_3_fixture_unstarted)

        # Act
        games_from_db = crud.get_games(filters)

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
        filters.append(models.GameModel.match_id == expected_game.match_id)
        db_util.save_game(expected_game)
        db_util.save_game(riot_fixtures.game_3_fixture_unstarted)

        # Act
        games_from_db = crud.get_games(filters)

        # Assert
        self.assertIsInstance(games_from_db, list)
        self.assertEqual(1, len(games_from_db))
        game_from_db = games_from_db[0]
        self.assertIsInstance(game_from_db, Game)
        self.assertEqual(expected_game, game_from_db)

    def test_get_game_by_id_existing_game(self):
        # Arrange
        expected_game = riot_fixtures.game_1_fixture_completed
        db_util.save_game(expected_game)

        # Act
        game_from_db = crud.get_game_by_id(expected_game.id)

        # Assert
        self.assertIsInstance(game_from_db, Game)
        self.assertEqual(expected_game, game_from_db)

    def test_get_game_by_id_no_existing_game(self):
        # Arrange
        expected_game = riot_fixtures.game_1_fixture_completed

        # Act
        game_from_db = crud.get_game_by_id(expected_game.id)

        # Assert
        self.assertIsNone(game_from_db)

    def test_get_games_to_check_status_inprogress_game(self):
        # Arrange
        match_in_past = riot_fixtures.match_fixture
        db_util.save_match(match_in_past)
        inprogress_game = riot_fixtures.game_2_fixture_inprogress
        db_util.save_game(inprogress_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(inprogress_game.id, game_ids[0])

    def test_get_games_to_check_status_unstarted_game(self):
        # Arrange
        match_in_past = riot_fixtures.match_fixture
        db_util.save_match(match_in_past)
        unstarted_game = riot_fixtures.game_3_fixture_unstarted
        db_util.save_game(unstarted_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(unstarted_game.id, game_ids[0])

    def test_get_games_to_check_status_completed_game(self):
        # Arrange
        match_in_past = riot_fixtures.match_fixture
        db_util.save_match(match_in_past)
        completed_game = riot_fixtures.game_1_fixture_completed
        db_util.save_game(completed_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unneeded_game(self):
        # Arrange
        match_in_past = riot_fixtures.match_fixture
        db_util.save_match(match_in_past)
        unneeded_game = riot_fixtures.game_4_fixture_unneeded
        db_util.save_game(unneeded_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_inprogress_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = riot_fixtures.future_match_fixture
        db_util.save_match(future_match)
        inprogress_game = riot_fixtures.game_2_fixture_inprogress
        db_util.save_game(inprogress_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unstarted_game_future_match(self):
        # Arrange
        future_match = riot_fixtures.future_match_fixture
        db_util.save_match(future_match)
        unstarted_game = riot_fixtures.game_3_fixture_unstarted
        db_util.save_game(unstarted_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_completed_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = riot_fixtures.future_match_fixture
        db_util.save_match(future_match)
        completed_game = riot_fixtures.game_1_fixture_completed
        db_util.save_game(completed_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_to_check_status_unneeded_game_future_match(self):
        # This shouldn't be possible, but testing the edge case
        # Arrange
        future_match = riot_fixtures.future_match_fixture
        db_util.save_match(future_match)
        unneeded_game = riot_fixtures.game_4_fixture_unneeded
        db_util.save_game(unneeded_game)

        # Act
        game_ids = crud.get_games_to_check_state()

        # Assert
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_update_game_state(self):
        # Arrange
        unstarted_game = riot_fixtures.game_3_fixture_unstarted
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
        game = riot_fixtures.game_4_fixture_unneeded
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
        expected_league = riot_fixtures.league_1_fixture

        # Act
        crud.save_league(expected_league)

        # Assert
        league_model_from_db = db_util.get_league_by_id(expected_league.id)
        league_from_db = schemas.League.model_validate(league_model_from_db)
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_no_filters(self):
        # Arrange
        expected_league = riot_fixtures.league_1_fixture
        db_util.save_league(expected_league)

        # Act
        leagues_from_db = crud.get_leagues()

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        league_from_db = leagues_from_db[0]
        self.assertIsInstance(league_from_db, League)
        self.assertEqual(expected_league, leagues_from_db[0])

    def test_get_leagues_empty_filters(self):
        # Arrange
        filters = []
        expected_league = riot_fixtures.league_1_fixture
        db_util.save_league(expected_league)

        # Act
        leagues_from_db = crud.get_leagues(filters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        league_from_db = leagues_from_db[0]
        self.assertIsInstance(league_from_db, League)
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_name_filter(self):
        # Arrange
        filters = []
        expected_league = riot_fixtures.league_1_fixture
        filters.append(models.LeagueModel.name == expected_league.name)
        db_util.save_league(expected_league)
        db_util.save_league(riot_fixtures.league_2_fixture)

        # Act
        leagues_from_db = crud.get_leagues(filters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        league_from_db = leagues_from_db[0]
        self.assertIsInstance(league_from_db, League)
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_name_filter_no_league(self):
        # Arrange
        filters = []
        expected_league = riot_fixtures.league_1_fixture
        filters.append(models.LeagueModel.name == expected_league.name)
        db_util.save_league(riot_fixtures.league_2_fixture)

        # Act
        leagues_from_db = crud.get_leagues(filters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(0, len(leagues_from_db))

    def test_get_leagues_region_filter(self):
        # Arrange
        filters = []
        expected_league = riot_fixtures.league_1_fixture
        filters.append(models.LeagueModel.region == expected_league.region)
        db_util.save_league(expected_league)
        db_util.save_league(riot_fixtures.league_2_fixture)

        # Act
        leagues_from_db = crud.get_leagues(filters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        league_from_db = leagues_from_db[0]
        self.assertIsInstance(league_from_db, League)
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_region_filter_no_league(self):
        # Arrange
        filters = []
        expected_league = riot_fixtures.league_1_fixture
        filters.append(models.LeagueModel.region == expected_league.region)
        db_util.save_league(riot_fixtures.league_2_fixture)

        # Act
        leagues_from_db = crud.get_leagues(filters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(0, len(leagues_from_db))

    def test_get_league_by_id_existing_league(self):
        # Arrange
        expected_league = riot_fixtures.league_1_fixture
        db_util.save_league(expected_league)

        # Act
        league_from_db = crud.get_league_by_id(expected_league.id)

        # Assert
        self.assertIsNotNone(league_from_db)
        self.assertIsInstance(league_from_db, League)
        self.assertEqual(expected_league, league_from_db)

    def test_get_league_by_id_no_existing_league(self):
        # Arrange
        expected_league = riot_fixtures.league_1_fixture

        # Act
        league_from_db = crud.get_league_by_id(expected_league.id)

        # Assert
        self.assertIsNone(league_from_db)

    def test_get_league_ids_for_player_successful(self):
        # Arrange
        db_util.save_league(riot_fixtures.league_1_fixture)
        db_util.save_league(riot_fixtures.league_2_fixture)
        db_util.save_team(riot_fixtures.team_1_fixture)
        db_util.save_team(riot_fixtures.team_2_fixture)
        db_util.save_player(riot_fixtures.player_1_fixture)

        # Act
        league_ids = crud.get_league_ids_for_player(riot_fixtures.player_1_fixture.id)

        # Assert
        self.assertIsInstance(league_ids, list)
        self.assertEqual(1, len(league_ids))
        self.assertEqual(riot_fixtures.league_1_fixture.id, league_ids[0])

    def test_get_league_ids_for_player_non_existing_player_id(self):
        # Arrange
        db_util.save_league(riot_fixtures.league_1_fixture)
        db_util.save_league(riot_fixtures.league_2_fixture)
        db_util.save_team(riot_fixtures.team_1_fixture)
        db_util.save_team(riot_fixtures.team_2_fixture)
        db_util.save_player(riot_fixtures.player_1_fixture)

        # Act
        league_ids = crud.get_league_ids_for_player("123")

        # Assert
        self.assertIsInstance(league_ids, list)
        self.assertEqual(0, len(league_ids))

    # --------------------------------------------------
    # ------------- Tournament Operations --------------
    # --------------------------------------------------
    def test_save_tournament(self):
        # Arrange
        expected_tournament = riot_fixtures.tournament_fixture

        # Act
        crud.save_tournament(expected_tournament)

        # Assert
        tournament_model_from_db = db_util.get_tournament_by_id(expected_tournament.id)
        self.assertIsNotNone(tournament_model_from_db)
        tournament_from_db = schemas.Tournament.model_validate(tournament_model_from_db)
        self.assertEqual(expected_tournament, tournament_from_db)

    def test_get_tournaments_empty_filters_existing_tournaments(self):
        # Arrange
        filters = []
        expected_tournament = riot_fixtures.tournament_fixture
        db_util.save_tournament(expected_tournament)

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(1, len(tournaments_from_db))
        tournament_from_db = tournaments_from_db[0]
        self.assertIsInstance(tournament_from_db, Tournament)
        self.assertEqual(expected_tournament, tournament_from_db)

    def test_get_tournaments_empty_filters_no_existing_tournaments(self):
        # Arrange
        filters = []

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(0, len(tournaments_from_db))

    def test_get_tournaments_start_date_filter_existing_tournament(self):
        # Arrange
        current_date = datetime.now()
        filters = [models.TournamentModel.start_date < current_date]
        expected_tournament = riot_fixtures.tournament_fixture
        db_util.save_tournament(expected_tournament)

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(1, len(tournaments_from_db))
        tournament_from_db = tournaments_from_db[0]
        self.assertIsInstance(tournament_from_db, Tournament)
        self.assertEqual(expected_tournament, tournament_from_db)

    def test_get_tournaments_start_date_filter_no_existing_tournament(self):
        # Arrange
        current_date = datetime.now()
        filters = [models.TournamentModel.start_date > current_date]
        expected_tournament = riot_fixtures.tournament_fixture
        db_util.save_tournament(expected_tournament)

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(0, len(tournaments_from_db))

    def test_get_tournaments_end_date_filter_existing_tournament(self):
        # Arrange
        current_date = datetime.now()
        filters = [models.TournamentModel.end_date < current_date]
        expected_tournament = riot_fixtures.tournament_fixture
        db_util.save_tournament(expected_tournament)

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(1, len(tournaments_from_db))
        tournament_from_db = tournaments_from_db[0]
        self.assertIsInstance(tournament_from_db, Tournament)
        self.assertEqual(expected_tournament, tournament_from_db)

    def test_get_tournaments_end_date_filter_no_existing_tournament(self):
        # Arrange
        current_date = datetime.now()
        filters = [models.TournamentModel.end_date > current_date]
        expected_tournament = riot_fixtures.tournament_fixture
        db_util.save_tournament(expected_tournament)

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(0, len(tournaments_from_db))

    def test_get_tournament_by_id_existing_tournament(self):
        # Arrange
        expected_tournament = riot_fixtures.tournament_fixture
        db_util.save_tournament(expected_tournament)

        # Act
        tournament_from_db = crud.get_tournament_by_id(expected_tournament.id)

        # Assert
        self.assertIsNotNone(tournament_from_db)
        self.assertIsInstance(tournament_from_db, Tournament)
        self.assertEqual(expected_tournament, tournament_from_db)

    def test_get_tournament_by_id_no_existing_tournament(self):
        # Arrange
        expected_tournament = riot_fixtures.tournament_fixture

        # Act
        tournament_from_db = crud.get_tournament_by_id(expected_tournament.id)

        # Assert
        self.assertIsNone(tournament_from_db)

    # --------------------------------------------------
    # --------------- Match Operations -----------------
    # --------------------------------------------------
    def test_save_match(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture

        # Act
        crud.save_match(expected_match)

        # Assert
        match_model_from_db = db_util.get_match_by_id(expected_match.id)
        self.assertIsNotNone(match_model_from_db)
        match_from_db = schemas.Match.model_validate(match_model_from_db)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_no_filters(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture
        db_util.save_match(expected_match)

        # Act
        matches_from_db = crud.get_matches()

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_empty_filters(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        db_util.save_match(expected_match)

        # Act
        matches_from_db = crud.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_league_slug_filter_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(models.MatchModel.league_slug == expected_match.league_slug)
        db_util.save_match(expected_match)

        # Act
        matches_from_db = crud.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_league_slug_filter_no_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(models.MatchModel.league_slug == "badFilter")
        db_util.save_match(expected_match)

        # Act
        matches_from_db = crud.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(0, len(matches_from_db))

    def test_get_matches_tournament_id_filter_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(models.MatchModel.tournament_id == expected_match.tournament_id)
        db_util.save_match(expected_match)

        # Act
        matches_from_db = crud.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_tournament_id_filter_no_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(models.MatchModel.tournament_id == "badFilter")
        db_util.save_match(expected_match)

        # Act
        matches_from_db = crud.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(0, len(matches_from_db))

    def test_get_match_by_id_existing_match(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture
        db_util.save_match(expected_match)

        # Act
        match_from_db = crud.get_match_by_id(expected_match.id)

        # Assert
        self.assertIsNotNone(match_from_db)
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_match_by_id_no_existing_match(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture

        # Act
        match_from_db = crud.get_match_by_id(expected_match.id)

        # Assert
        self.assertIsNone(match_from_db)

    def test_get_match_ids_without_games_matches_with_no_games(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture
        game_for_future_match = riot_fixtures.game_1_fixture_unstarted_future_match
        db_util.save_match(expected_match)
        db_util.save_game(game_for_future_match)

        # Act
        match_ids_without_games = crud.get_match_ids_without_games()

        # Assert
        self.assertNotEqual(game_for_future_match.match_id, expected_match.id)
        self.assertIsInstance(match_ids_without_games, list)
        self.assertEqual(1, len(match_ids_without_games))
        self.assertEqual(expected_match.id, match_ids_without_games[0])

    def test_get_match_ids_without_games_matches_with_games(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture
        db_util.save_match(expected_match)
        game = riot_fixtures.game_1_fixture_completed
        db_util.save_game(game)

        # Act
        match_ids_without_games = crud.get_match_ids_without_games()

        # Assert
        self.assertEqual(game.match_id, expected_match.id)
        self.assertIsInstance(match_ids_without_games, list)
        self.assertEqual(0, len(match_ids_without_games))

    # --------------------------------------------------
    # ---------------- Team Operations ----------------
    # --------------------------------------------------
    def test_save_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture

        # Act
        crud.save_team(expected_team)

        # Assert
        team_model_from_db = db_util.get_team_by_id(expected_team.id)
        team_from_db = schemas.ProfessionalTeam.model_validate(team_model_from_db)
        self.assertEqual(expected_team, team_from_db)

    def test_get_teams_no_filters(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        db_util.save_team(expected_team)

        # Act
        teams_from_db = crud.get_teams()

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(1, len(teams_from_db))
        team_from_db = teams_from_db[0]
        self.assertIsInstance(team_from_db, ProfessionalTeam)
        self.assertEqual(expected_team, team_from_db)

    def test_get_teams_empty_filters(self):
        # Arrange
        filters = []
        expected_team = riot_fixtures.team_1_fixture
        db_util.save_team(expected_team)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(1, len(teams_from_db))
        team_from_db = teams_from_db[0]
        self.assertIsInstance(team_from_db, ProfessionalTeam)
        self.assertEqual(expected_team, team_from_db)

    def test_get_teams_name_filter_existing_team(self):
        # Arrange
        filters = []
        expected_team = riot_fixtures.team_1_fixture
        filters.append(models.ProfessionalTeamModel.name == expected_team.name)
        db_util.save_team(expected_team)
        db_util.save_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(1, len(teams_from_db))
        team_from_db = teams_from_db[0]
        self.assertIsInstance(team_from_db, ProfessionalTeam)
        self.assertEqual(expected_team, team_from_db)

    def test_get_teams_name_filter_no_existing_team(self):
        # Arrange
        filters = []
        team_1 = riot_fixtures.team_1_fixture
        filters.append(models.ProfessionalTeamModel.name == team_1.name)
        db_util.save_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(0, len(teams_from_db))

    def test_get_teams_slug_filter_existing_team(self):
        # Arrange
        filters = []
        expected_team = riot_fixtures.team_1_fixture
        filters.append(models.ProfessionalTeamModel.slug == expected_team.slug)
        db_util.save_team(expected_team)
        db_util.save_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(1, len(teams_from_db))
        team_from_db = teams_from_db[0]
        self.assertIsInstance(team_from_db, ProfessionalTeam)
        self.assertEqual(expected_team, team_from_db)

    def test_get_teams_slug_filter_no_existing_team(self):
        # Arrange
        filters = []
        team_1 = riot_fixtures.team_1_fixture
        filters.append(models.ProfessionalTeamModel.slug == team_1.slug)
        db_util.save_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(0, len(teams_from_db))

    def test_get_teams_code_filter_existing_team(self):
        # Arrange
        filters = []
        expected_team = riot_fixtures.team_1_fixture
        filters.append(models.ProfessionalTeamModel.code == expected_team.code)
        db_util.save_team(expected_team)
        db_util.save_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(1, len(teams_from_db))
        team_from_db = teams_from_db[0]
        self.assertIsInstance(team_from_db, ProfessionalTeam)
        self.assertEqual(expected_team, team_from_db)

    def test_get_teams_code_filter_no_existing_team(self):
        # Arrange
        filters = []
        team_1 = riot_fixtures.team_1_fixture
        filters.append(models.ProfessionalTeamModel.code == team_1.code)
        db_util.save_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(0, len(teams_from_db))

    def test_get_teams_status_filter_existing_team(self):
        # Arrange
        filters = []
        expected_team = riot_fixtures.team_1_fixture
        filters.append(models.ProfessionalTeamModel.status == expected_team.status)
        db_util.save_team(expected_team)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(1, len(teams_from_db))
        team_from_db = teams_from_db[0]
        self.assertIsInstance(team_from_db, ProfessionalTeam)
        self.assertEqual(expected_team, team_from_db)

    def test_get_teams_status_filter_no_existing_team(self):
        # Arrange
        filters = []
        team_1 = riot_fixtures.team_1_fixture
        filters.append(models.ProfessionalTeamModel.status == team_1.status)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(0, len(teams_from_db))

    def test_get_teams_league_filter_existing_team(self):
        # Arrange
        filters = []
        expected_team = riot_fixtures.team_1_fixture
        filters.append(models.ProfessionalTeamModel.home_league == expected_team.home_league)
        db_util.save_team(expected_team)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(1, len(teams_from_db))
        team_from_db = teams_from_db[0]
        self.assertIsInstance(team_from_db, ProfessionalTeam)
        self.assertEqual(expected_team, team_from_db)

    def test_get_teams_league_filter_no_existing_team(self):
        # Arrange
        filters = []
        team_1 = riot_fixtures.team_1_fixture
        filters.append(models.ProfessionalTeamModel.home_league == team_1.home_league)

        # Act
        teams_from_db = crud.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(0, len(teams_from_db))

    def test_get_team_by_id_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        db_util.save_team(expected_team)

        # Act
        team_from_db = crud.get_team_by_id(expected_team.id)

        # Assert
        self.assertIsNotNone(team_from_db)
        self.assertIsInstance(team_from_db, ProfessionalTeam)
        self.assertEqual(expected_team, team_from_db)

    def test_get_team_from_id_no_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture

        # Act
        team_from_db = crud.get_team_by_id(expected_team.id)

        # Assert
        self.assertIsNone(team_from_db)

    # --------------------------------------------------
    # ---------- Fantasy League Operations -------------
    # --------------------------------------------------
    def test_create_fantasy_league(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture

        # Act
        crud.create_fantasy_league(fantasy_league)

        # Assert
        fantasy_league_model_from_db = db_util.get_fantasy_league_by_id(fantasy_league.id)
        fantasy_league_from_db = fantasy_league.model_validate(fantasy_league_model_from_db)
        self.assertEqual(fantasy_league, fantasy_league_from_db)

    def test_create_fantasy_league_with_an_existing_id(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(IntegrityError) as context:
            crud.create_fantasy_league(fantasy_league)
        self.assertIn('UNIQUE constraint failed: fantasy_leagues.id', str(context.exception))

    def test_get_fantasy_league_by_id_existing_fantasy_league(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)

        # Act
        fantasy_league_model_from_db = crud.get_fantasy_league_by_id(fantasy_league.id)

        # Assert
        self.assertIsNotNone(fantasy_league_model_from_db)
        fantasy_league_from_db = fantasy_schemas.FantasyLeague.model_validate(
            fantasy_league_model_from_db
        )
        self.assertEqual(fantasy_league, fantasy_league_from_db)

    def test_get_fantasy_league_by_id_no_existing_fantasy_league(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture

        # Act
        fantasy_league_model_from_db = crud.get_fantasy_league_by_id(fantasy_league.id)

        # Assert
        self.assertIsNone(fantasy_league_model_from_db)

    def test_update_fantasy_league_settings_name(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        updated_fantasy_league_settings = copy.deepcopy(
            fantasy_fixtures.fantasy_league_settings_fixture
        )
        updated_fantasy_league_settings.name = "Updated Fantasy League name"

        # Act
        updated_fantasy_league_model = crud.update_fantasy_league_settings(
            fantasy_league.id, updated_fantasy_league_settings
        )

        # Assert
        self.assertEqual(updated_fantasy_league_settings.name, updated_fantasy_league_model.name)
        self.assertEqual(
            updated_fantasy_league_model.number_of_teams, fantasy_league.number_of_teams
        )
        self.assertEqual(
            updated_fantasy_league_model.available_leagues, fantasy_league.available_leagues
        )
        self.assertNotEqual(updated_fantasy_league_settings.name, fantasy_league.name)

    def test_update_fantasy_league_settings_number_of_teams(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        updated_fantasy_league_settings = copy.deepcopy(
            fantasy_fixtures.fantasy_league_settings_fixture
        )
        updated_fantasy_league_settings.number_of_teams = 4

        # Act
        updated_fantasy_league_model = crud.update_fantasy_league_settings(
            fantasy_league.id, updated_fantasy_league_settings
        )

        # Assert
        self.assertEqual(
            updated_fantasy_league_settings.number_of_teams,
            updated_fantasy_league_model.number_of_teams
        )
        self.assertEqual(
            updated_fantasy_league_model.name, fantasy_league.name
        )
        self.assertEqual(
            updated_fantasy_league_model.available_leagues, fantasy_league.available_leagues
        )
        self.assertNotEqual(
            updated_fantasy_league_settings.number_of_teams,
            fantasy_league.number_of_teams
        )

    def test_update_fantasy_league_settings_available_leagues(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        updated_fantasy_league_settings = copy.deepcopy(
            fantasy_fixtures.fantasy_league_settings_fixture
        )
        updated_fantasy_league_settings.available_leagues = ["RiotLeague1"]

        # Act
        updated_fantasy_league_model = crud.update_fantasy_league_settings(
            fantasy_league.id, updated_fantasy_league_settings
        )

        # Assert
        self.assertEqual(
            updated_fantasy_league_settings.available_leagues,
            updated_fantasy_league_model.available_leagues
        )
        self.assertEqual(
            updated_fantasy_league_model.name, fantasy_league.name
        )
        self.assertEqual(
            updated_fantasy_league_model.number_of_teams, fantasy_league.number_of_teams
        )
        self.assertNotEqual(
            updated_fantasy_league_settings.available_leagues,
            fantasy_league.available_leagues
        )

    # --------------------------------------------------
    # ----------- Fantasy Team Operations --------------
    # --------------------------------------------------

    def test_create_fantasy_team(self):
        # Arrange
        fantasy_team = fantasy_fixtures.fantasy_team_week_1

        # act
        crud.create_or_update_fantasy_team(fantasy_team)

        # Assert
        fantasy_teams_from_db = db_util.get_all_fantasy_teams()
        self.assertIsInstance(fantasy_teams_from_db, list)
        self.assertEqual(1, len(fantasy_teams_from_db))
        self.assertEqual(
            fantasy_team,
            fantasy_schemas.FantasyTeam.model_validate(fantasy_teams_from_db[0])
        )

    def test_update_fantasy_team(self):
        # Arrange
        fantasy_team = fantasy_fixtures.fantasy_team_week_1
        crud.create_or_update_fantasy_team(fantasy_team)
        modified_team = copy.deepcopy(fantasy_team)
        modified_team.top_player_id = '1234'

        # act
        crud.create_or_update_fantasy_team(modified_team)

        # Assert
        fantasy_teams_from_db = db_util.get_all_fantasy_teams()
        self.assertIsInstance(fantasy_teams_from_db, list)
        self.assertEqual(1, len(fantasy_teams_from_db))
        self.assertEqual(
            modified_team,
            fantasy_schemas.FantasyTeam.model_validate(fantasy_teams_from_db[0])
        )

    def test_get_all_fantasy_teams_for_user(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_active_fixture
        user = fantasy_fixtures.user_fixture
        fantasy_team_week_1 = fantasy_fixtures.fantasy_team_week_1
        crud.create_or_update_fantasy_team(fantasy_team_week_1)
        fantasy_team_week_2 = fantasy_fixtures.fantasy_team_week_2
        crud.create_or_update_fantasy_team(fantasy_team_week_2)

        # Act
        fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(fantasy_league.id, user.id)

        # Assert
        self.assertIsInstance(fantasy_teams_from_db, list)
        self.assertEqual(2, len(fantasy_teams_from_db))
        fantasy_teams_from_db.sort(key=lambda x: x.week)
        self.assertEqual(
            fantasy_team_week_1,
            fantasy_schemas.FantasyTeam.model_validate(fantasy_teams_from_db[0])
        )
        self.assertEqual(
            fantasy_team_week_2,
            fantasy_schemas.FantasyTeam.model_validate(fantasy_teams_from_db[1])
        )

    def test_get_all_fantasy_teams_for_user_bad_fantasy_league_id(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_team_week_1 = fantasy_fixtures.fantasy_team_week_1
        crud.create_or_update_fantasy_team(fantasy_team_week_1)

        # Act
        fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user("badLeagueId", user.id)

        # Assert
        self.assertIsInstance(fantasy_teams_from_db, list)
        self.assertEqual(0, len(fantasy_teams_from_db))

    def test_get_all_fantasy_teams_for_user_bad_user_id(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        fantasy_team_week_1 = fantasy_fixtures.fantasy_team_week_1
        crud.create_or_update_fantasy_team(fantasy_team_week_1)

        # Act
        fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(fantasy_league.id, "badUserId")

        # Assert
        self.assertIsInstance(fantasy_teams_from_db, list)
        self.assertEqual(0, len(fantasy_teams_from_db))
