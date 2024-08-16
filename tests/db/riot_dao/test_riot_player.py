from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.schemas.riot_data_schemas import ProfessionalPlayer
from src.db.models import ProfessionalPlayerModel


class TestCrudRiotPlayer(TestBase):
    def test_put_player_no_existing_player(self):
        # Arrange
        player = riot_fixtures.player_1_fixture

        # Act and Assert
        player_before_put = self.db.get_player_by_id(player.id)
        self.assertIsNone(player_before_put)
        self.db.put_player(player)
        player_after_put = self.db.get_player_by_id(player.id)
        self.assertEqual(player, player_after_put)

    def test_put_player_existing_player(self):
        # Arrange
        player = riot_fixtures.player_1_fixture
        self.db.put_player(player)
        updated_player = player.model_copy(deep=True)
        updated_player.image = "updatedImage"

        # Act and Assert
        player_before_put = self.db.get_player_by_id(player.id)
        self.assertEqual(player, player_before_put)
        self.assertEqual(player.id, updated_player.id)
        self.db.put_player(updated_player)
        player_after_put = self.db.get_player_by_id(player.id)
        self.assertEqual(updated_player, player_after_put)

    def test_get_players_no_filters(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)

        # Act
        players_from_db = self.db.get_players()

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        player_from_db = players_from_db[0]
        self.assertIsInstance(player_from_db, ProfessionalPlayer)
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_empty_filters(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)

        # Act
        players_from_db = self.db.get_players(filters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        player_from_db = players_from_db[0]
        self.assertIsInstance(player_from_db, ProfessionalPlayer)
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_summoner_name_filter_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_6_fixture
        filters.append(ProfessionalPlayerModel.summoner_name == expected_player.summoner_name)
        self.db.put_player(expected_player)
        self.db.put_player(other_player)

        # Act
        players_from_db = self.db.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player, other_player)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        player_from_db = players_from_db[0]
        self.assertIsInstance(player_from_db, ProfessionalPlayer)
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_summoner_name_filter_no_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_6_fixture
        filters.append(ProfessionalPlayerModel.summoner_name == expected_player.summoner_name)
        self.db.put_player(other_player)

        # Act
        players_from_db = self.db.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player.summoner_name, other_player.summoner_name)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_players_team_id_filter_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_6_fixture
        filters.append(ProfessionalPlayerModel.team_id == expected_player.team_id)
        self.db.put_player(expected_player)
        self.db.put_player(other_player)

        # Act
        players_from_db = self.db.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player, other_player)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        player_from_db = players_from_db[0]
        self.assertIsInstance(player_from_db, ProfessionalPlayer)
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_team_id_filter_no_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_6_fixture
        filters.append(ProfessionalPlayerModel.team_id == expected_player.team_id)
        self.db.put_player(other_player)

        # Act
        players_from_db = self.db.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player.team_id, other_player.team_id)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_players_role_filter_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_7_fixture
        filters.append(ProfessionalPlayerModel.role == expected_player.role)
        self.db.put_player(expected_player)
        self.db.put_player(other_player)

        # Act
        players_from_db = self.db.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player, other_player)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        player_from_db = players_from_db[0]
        self.assertIsInstance(player_from_db, ProfessionalPlayer)
        self.assertEqual(expected_player, player_from_db)

    def test_get_players_role_filter_no_existing_player(self):
        # Arrange
        filters = []
        expected_player = riot_fixtures.player_1_fixture
        other_player = riot_fixtures.player_7_fixture
        filters.append(ProfessionalPlayerModel.role == expected_player.role)
        self.db.put_player(other_player)

        # Act
        players_from_db = self.db.get_players(filters)

        # Assert
        self.assertNotEqual(expected_player.role, other_player.role)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_player_by_id_existing_player(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)

        # Act
        player_from_db = self.db.get_player_by_id(expected_player.id)

        # Assert
        self.assertIsNotNone(player_from_db)
        self.assertIsInstance(player_from_db, ProfessionalPlayer)
        self.assertEqual(expected_player, player_from_db)

    def test_get_player_by_id_no_existing_player(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture

        # Act
        player_from_db = self.db.get_player_by_id(expected_player.id)

        # Assert
        self.assertIsNone(player_from_db)
