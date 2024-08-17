from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.exceptions import ProfessionalPlayerNotFoundException
from src.common.schemas.search_parameters import PlayerSearchParameters
from src.common.schemas.riot_data_schemas import ProPlayerID
from src.riot.service import RiotProfessionalPlayerService


class ProfessionalPlayerServiceTest(TestBase):
    def setUp(self):
        super().setUp()
        self.professional_player_service = RiotProfessionalPlayerService(self.db)

    def test_get_existing_professional_players_by_summoner_name(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        search_parameters = PlayerSearchParameters(summoner_name=expected_player.summoner_name)

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_summoner_name(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        search_parameters = PlayerSearchParameters(summoner_name="badSummonerName")

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_existing_professional_players_by_role(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        search_parameters = PlayerSearchParameters(role=expected_player.role)

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_role(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        search_parameters = PlayerSearchParameters(role="none")

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_existing_professional_players_by_team_id(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        search_parameters = PlayerSearchParameters(team_id=expected_player.team_id)

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_team_id(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        search_parameters = PlayerSearchParameters(team_id="777")

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_professional_player_by_id(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)

        # Act
        player_from_db = self.professional_player_service.get_player_by_id(expected_player.id)

        # Assert
        self.assertEqual(player_from_db, expected_player)

    def test_get_professional_player_by_id_invalid_id(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)

        # Act and Assert
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            self.professional_player_service.get_player_by_id(ProPlayerID("777"))
