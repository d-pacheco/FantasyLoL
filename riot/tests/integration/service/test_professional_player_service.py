from ...test_base import FantasyLolTestBase
from ...test_util import riot_data_util

from riot.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from riot.service.riot_professional_player_service import RiotProfessionalPlayerService
from common.schemas.search_parameters import PlayerSearchParameters


def create_professional_player_service():
    return RiotProfessionalPlayerService()


class ProfessionalPlayerServiceTest(FantasyLolTestBase):
    def test_get_existing_professional_players_by_summoner_name(self):
        # Arrange
        professional_player_service = create_professional_player_service()
        expected_player = riot_data_util.create_professional_player_in_db()
        search_parameters = PlayerSearchParameters(summoner_name=expected_player.summoner_name)

        # Act
        players_from_db = professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_summoner_name(self):
        # Arrange
        professional_player_service = create_professional_player_service()
        riot_data_util.create_professional_player_in_db()
        search_parameters = PlayerSearchParameters(summoner_name="badSummonerName")

        # Act
        players_from_db = professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_existing_professional_players_by_role(self):
        # Arrange
        professional_player_service = create_professional_player_service()
        expected_player = riot_data_util.create_professional_player_in_db()
        search_parameters = PlayerSearchParameters(role=expected_player.role)

        # Act
        players_from_db = professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_role(self):
        # Arrange
        professional_player_service = create_professional_player_service()
        riot_data_util.create_professional_player_in_db()
        search_parameters = PlayerSearchParameters(role="badRole")

        # Act
        players_from_db = professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_existing_professional_players_by_team_id(self):
        # Arrange
        professional_player_service = create_professional_player_service()
        expected_player = riot_data_util.create_professional_player_in_db()
        search_parameters = PlayerSearchParameters(team_id=expected_player.team_id)

        # Act
        players_from_db = professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_team_id(self):
        # Arrange
        professional_player_service = create_professional_player_service()
        riot_data_util.create_professional_player_in_db()
        search_parameters = PlayerSearchParameters(team_id="777")

        # Act
        players_from_db = professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_professional_player_by_id(self):
        # Arrange
        professional_player_service = create_professional_player_service()
        expected_player = riot_data_util.create_professional_player_in_db()

        # Act
        player_from_db = professional_player_service.get_player_by_id(expected_player.id)

        # Assert
        self.assertEqual(player_from_db, expected_player)

    def test_get_professional_player_by_id_invalid_id(self):
        # Arrange
        professional_player_service = create_professional_player_service()
        riot_data_util.create_professional_player_in_db()

        # Act and Assert
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            professional_player_service.get_player_by_id("777")
