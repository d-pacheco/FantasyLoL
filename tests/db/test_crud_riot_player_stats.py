from src.common.schemas.riot_data_schemas import PlayerGameStats, RiotGameID
from src.db import crud
from src.db.views import PlayerGameView
from tests.test_base import FantasyLolTestBase
from tests.test_util import riot_fixtures


class TestCrudRiotPlayerStats(FantasyLolTestBase):
    def test_put_player_stats_no_existing_stats(self):
        # Arrange
        player_stats = riot_fixtures.player_1_game_stats_fixture

        # Act and Assert
        player_stats_before_put = crud.get_player_stats(
            player_stats.game_id, player_stats.participant_id
        )
        self.assertIsNone(player_stats_before_put)
        crud.put_player_stats(player_stats)
        player_stats_after_put = crud.get_player_stats(
            player_stats.game_id, player_stats.participant_id
        )
        self.assertEqual(player_stats, player_stats_after_put)

    def test_put_player_stats_existing_stats(self):
        # Arrange
        player_stats = riot_fixtures.player_1_game_stats_fixture
        crud.put_player_stats(player_stats)
        updated_player_stats = player_stats.model_copy(deep=True)
        updated_player_stats.wards_placed += 1

        # Act and Assert
        player_stats_before_put = crud.get_player_stats(
            player_stats.game_id, player_stats.participant_id
        )
        self.assertEqual(player_stats, player_stats_before_put)
        self.assertEqual(player_stats.game_id, updated_player_stats.game_id)
        self.assertEqual(player_stats.participant_id, updated_player_stats.participant_id)
        crud.put_player_stats(updated_player_stats)
        player_stats_after_put = crud.get_player_stats(
            player_stats.game_id, player_stats.participant_id
        )
        self.assertEqual(updated_player_stats, player_stats_after_put)

    def test_get_player_stats(self):
        # Arrange
        player_stats = riot_fixtures.player_1_game_stats_fixture
        crud.put_player_stats(player_stats)

        # Act and Assert
        self.assertEqual(
            player_stats,
            crud.get_player_stats(player_stats.game_id, player_stats.participant_id)
        )
        self.assertIsNone(crud.get_player_stats(RiotGameID("123"), player_stats.participant_id))
        self.assertIsNone(crud.get_player_stats(player_stats.game_id, 123))

    def test_get_game_ids_to_fetch_player_stats_for_completed_game_without_10_rows(self):
        game = riot_fixtures.game_1_fixture_completed
        crud.put_game(game)
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_game_ids_to_fetch_player_stats_for_completed_game_with_10_rows(self):
        game = riot_fixtures.game_1_fixture_completed
        crud.put_game(game)
        for participant_id in range(1, 11):
            create_player_stats(game.id, participant_id)
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_game_ids_to_fetch_player_stats_for_inprogress_game_without_10_rows(self):
        game = riot_fixtures.game_2_fixture_inprogress
        crud.put_game(game)
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_game_ids_to_fetch_player_stats_for_inprogress_game_with_10_rows(self):
        game = riot_fixtures.game_2_fixture_inprogress
        crud.put_game(game)
        for participant_id in range(1, 11):
            create_player_stats(game.id, participant_id)
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_game_ids_to_fetch_player_stats_for_unstarted_game_without_10_rows(self):
        game = riot_fixtures.game_3_fixture_unstarted
        crud.put_game(game)
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_player_game_stats_no_filters(self):
        # Arrange
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        crud.put_player_metadata(riot_fixtures.player_1_game_metadata_fixture)
        crud.put_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        players_game_data_from_db = crud.get_player_game_stats()

        # Assert
        self.assertIsInstance(players_game_data_from_db, list)
        self.assertEqual(1, len(players_game_data_from_db))
        player_game_data_from_db = players_game_data_from_db[0]
        self.assertEqual(expected_player_game_data, player_game_data_from_db)

    def test_get_player_game_stats_empty_filter(self):
        # Arrange
        filters = []
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        crud.put_player_metadata(riot_fixtures.player_1_game_metadata_fixture)
        crud.put_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        players_game_data_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(players_game_data_from_db, list)
        self.assertEqual(1, len(players_game_data_from_db))
        player_game_data_from_db = players_game_data_from_db[0]
        self.assertEqual(expected_player_game_data, player_game_data_from_db)

    def test_get_player_game_stats_has_metadata_but_no_stats(self):
        # Arrange
        filters = []
        crud.put_player_metadata(riot_fixtures.player_1_game_metadata_fixture)

        # Act
        players_game_data_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(players_game_data_from_db, list)
        self.assertEqual(0, len(players_game_data_from_db))

    def test_get_player_game_stats_has_stats_but_no_metadata(self):
        # Arrange
        filters = []
        crud.put_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        players_game_data_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(players_game_data_from_db, list)
        self.assertEqual(0, len(players_game_data_from_db))

    def test_get_player_game_stats_game_id_filter_existing_stats(self):
        # Arrange
        filters = []
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        filters.append(PlayerGameView.game_id == expected_player_game_data.game_id)
        crud.put_player_metadata(riot_fixtures.player_1_game_metadata_fixture)
        crud.put_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        players_game_data_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(players_game_data_from_db, list)
        self.assertEqual(1, len(players_game_data_from_db))
        player_game_data_from_db = players_game_data_from_db[0]
        self.assertEqual(expected_player_game_data, player_game_data_from_db)

    def test_get_player_game_stats_game_id_filter_no_existing_stats(self):
        # Arrange
        filters = []
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        filters.append(PlayerGameView.game_id == expected_player_game_data.game_id)

        # Act
        players_game_data_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(players_game_data_from_db, list)
        self.assertEqual(0, len(players_game_data_from_db))

    def test_get_player_game_stats_player_id_filter_existing_stats(self):
        # Arrange
        filters = []
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        filters.append(PlayerGameView.player_id == expected_player_game_data.player_id)
        crud.put_player_metadata(riot_fixtures.player_1_game_metadata_fixture)
        crud.put_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        players_game_data_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(players_game_data_from_db, list)
        self.assertEqual(1, len(players_game_data_from_db))
        player_game_data_from_db = players_game_data_from_db[0]
        self.assertEqual(expected_player_game_data, player_game_data_from_db)

    def test_get_player_game_stats_player_id_filter_no_existing_stats(self):
        # Arrange
        filters = []
        expected_player_game_data = riot_fixtures.player_1_game_data_fixture
        filters.append(PlayerGameView.player_id == expected_player_game_data.player_id)
        crud.put_player_metadata(riot_fixtures.player_1_game_metadata_fixture)
        crud.put_player_stats(riot_fixtures.player_1_game_stats_fixture)

        # Act
        players_game_data_from_db = crud.get_player_game_stats(filters)

        # Assert
        self.assertIsInstance(players_game_data_from_db, list)
        self.assertEqual(1, len(players_game_data_from_db))
        player_game_data_from_db = players_game_data_from_db[0]
        self.assertEqual(expected_player_game_data, player_game_data_from_db)


def create_player_stats(game_id: RiotGameID, participant_id: int):
    player_game_stats = PlayerGameStats(
        game_id=game_id,
        participant_id=participant_id,
        kills=1,
        deaths=1,
        assists=1,
        total_gold=10000,
        creep_score=100,
        kill_participation=int(0.5),
        champion_damage_share=int(0.2),
        wards_placed=10,
        wards_destroyed=10
    )
    crud.put_player_stats(player_game_stats)
