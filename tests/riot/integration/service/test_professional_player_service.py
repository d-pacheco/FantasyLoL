from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.exceptions import ProfessionalPlayerNotFoundException
from src.common.schemas.search_parameters import PlayerSearchParameters
from src.common.schemas.riot_data_schemas import ProPlayerID
from src.riot.service import RiotProfessionalPlayerService


class ProfessionalPlayerServiceTest(TestBase):
    def setUp(self):
        super().setUp()
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)
        self.professional_player_service = RiotProfessionalPlayerService(self.db)

    def test_get_existing_professional_players_by_summoner_name(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        # Partial, case-insensitive search
        search_parameters = PlayerSearchParameters(
            summoner_name=expected_player.summoner_name[:5].lower()
        )

        # Act
        players_from_db = self.professional_player_service.get_players(search_parameters)

        # Assert
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player.id, players_from_db[0].id)

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
        self.assertEqual(riot_fixtures.league_1_fixture.name, player.league_name)

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

    def test_team_filter_matches_by_team_code(self):
        # Arrange
        expected_player = riot_fixtures.player_1_fixture
        self.db.put_player(expected_player)
        # Search by team code
        search_parameters = PlayerSearchParameters(
            team_name=riot_fixtures.team_1_fixture.code
        )

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

    def test_active_only_excludes_archived_team_players(self):
        # Arrange
        from src.common.schemas.riot_data_schemas import ProfessionalTeam, ProTeamID

        archived_team = ProfessionalTeam(
            id=ProTeamID("archived-team-id"),
            slug="archived-team",
            name="Archived Team",
            code="ARC",
            image="http://arc.png",
            status="archived",
            home_league_name=riot_fixtures.league_1_fixture.name,
            home_league_region="MOCKED REGION",
        )
        self.db.put_team(archived_team)

        from src.common.schemas.riot_data_schemas import ProfessionalPlayer, ProPlayerID, PlayerRole

        archived_player = ProfessionalPlayer(
            id=ProPlayerID("archived-player-id"),
            summoner_name="ArchivedPlayer",
            image="http://archived.png",
            role=PlayerRole.MID,
            team_id=archived_team.id,
            team_name=archived_team.name,
            team_code=archived_team.code,
        )
        self.db.put_player(archived_player)

        active_player = riot_fixtures.player_1_fixture
        self.db.put_player(active_player)

        # Act - active_only=True (default)
        search_parameters = PlayerSearchParameters()
        players = self.professional_player_service.get_players(search_parameters)

        # Assert - only active team player returned
        player_ids = [p.id for p in players]
        self.assertIn(active_player.id, player_ids)
        self.assertNotIn(archived_player.id, player_ids)

    def test_active_only_false_includes_archived_team_players(self):
        # Arrange
        from src.common.schemas.riot_data_schemas import ProfessionalTeam, ProTeamID

        archived_team = ProfessionalTeam(
            id=ProTeamID("archived-team-id-2"),
            slug="archived-team-2",
            name="Archived Team 2",
            code="AR2",
            image="http://arc2.png",
            status="archived",
            home_league_name=riot_fixtures.league_1_fixture.name,
            home_league_region="MOCKED REGION",
        )
        self.db.put_team(archived_team)

        from src.common.schemas.riot_data_schemas import ProfessionalPlayer, ProPlayerID, PlayerRole

        archived_player = ProfessionalPlayer(
            id=ProPlayerID("archived-player-id-2"),
            summoner_name="ArchivedPlayer2",
            image="http://archived2.png",
            role=PlayerRole.TOP,
            team_id=archived_team.id,
            team_name=archived_team.name,
            team_code=archived_team.code,
        )
        self.db.put_player(archived_player)

        # Act - active_only=False
        search_parameters = PlayerSearchParameters(active_only=False)
        players = self.professional_player_service.get_players(search_parameters)

        # Assert - archived player is included
        player_ids = [p.id for p in players]
        self.assertIn(archived_player.id, player_ids)

    def test_fantasy_available_join_is_case_insensitive(self):
        """League name 'Mock League 1' should match team home_league_name 'MOCK LEAGUE 1'."""
        # Arrange
        from src.common.schemas.riot_data_schemas import (
            ProfessionalTeam,
            ProfessionalPlayer,
            ProTeamID,
            ProPlayerID,
            PlayerRole,
            League,
        )
        from src.common.schemas.riot_data_schemas import RiotLeagueID

        # Create a league with lowercase name
        league = League(
            id=RiotLeagueID("case-test-league-id"),
            name="case test league",
            slug="case-test",
            region="TEST",
            image="http://test.png",
            priority=99,
            fantasy_available=True,
        )
        self.db.put_league(league)

        # Create a team with UPPERCASE home_league_name
        team = ProfessionalTeam(
            id=ProTeamID("case-test-team-id"),
            slug="case-team",
            name="Case Team",
            code="CST",
            image="http://cst.png",
            status="active",
            home_league_name="CASE TEST LEAGUE",
            home_league_region="TEST",
        )
        self.db.put_team(team)

        player = ProfessionalPlayer(
            id=ProPlayerID("case-test-player-id"),
            summoner_name="CasePlayer",
            image="http://caseplayer.png",
            role=PlayerRole.MID,
            team_id=team.id,
            team_name=team.name,
            team_code=team.code,
        )
        self.db.put_player(player)

        # Act
        search_parameters = PlayerSearchParameters(fantasy_available=True, active_only=False)
        players = self.professional_player_service.get_players(search_parameters)

        # Assert - player found despite case mismatch in league name
        player_ids = [p.id for p in players]
        self.assertIn(player.id, player_ids)
