from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.exceptions import ProfessionalPlayerNotFoundException
from src.common.schemas.search_parameters import PlayerSearchParameters
from src.common.schemas.riot_data_schemas import ProPlayerID
from src.riot.service import RiotProfessionalPlayerService


class ProfessionalPlayerServiceTest(TestBase):
    def setUp(self):
        super().setUp()
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)
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

    def test_player_response_includes_team_name_and_code(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        search_parameters = PlayerSearchParameters()

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertEqual(1, len(players_from_db))
        player = players_from_db[0]
        self.assertEqual(riot_fixtures.team_1_fixture.name, player.team_name)
        self.assertEqual(riot_fixtures.team_1_fixture.code, player.team_code)

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
        search_parameters = PlayerSearchParameters(team_name=riot_fixtures.team_1_fixture.name)

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player.id, players_from_db[0].id)

    def test_get_no_existing_professional_players_by_team_id(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        search_parameters = PlayerSearchParameters(team_name="Nonexistent Team")

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_team_name_filter_is_case_insensitive_partial_match(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        # Use lowercase partial match of team name
        partial = riot_fixtures.team_1_fixture.name[:4].lower()
        search_parameters = PlayerSearchParameters(team_name=partial)

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player.id, players_from_db[0].id)

    def test_fantasy_available_filter_returns_only_players_in_fantasy_leagues(self):
        # Arrange
        # league_1 has fantasy_available=False, league_2 has fantasy_available=True
        league_2 = riot_fixtures.league_2_fixture
        self.db.put_league(league_2)

        # team_1 is in league_1 (not fantasy), team_2's home_league matches league_2
        team_2 = riot_fixtures.team_2_fixture.model_copy(deep=True)
        team_2.home_league_name = league_2.name
        self.db.put_team(team_2)

        player_in_fantasy = riot_fixtures.player_6_fixture
        self.db.put_player(player_in_fantasy)

        player_not_in_fantasy = riot_fixtures.player_1_fixture
        self.db.put_player(player_not_in_fantasy)

        search_parameters = PlayerSearchParameters(fantasy_available=True)

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(player_in_fantasy.id, players_from_db[0].id)

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
