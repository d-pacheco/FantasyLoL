from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.schemas.search_parameters import TeamSearchParameters
from src.common.schemas.riot_data_schemas import ProTeamID
from src.riot.exceptions import ProfessionalTeamNotFoundException
from src.riot.service import RiotProfessionalTeamService


class ProfessionalTeamServiceTest(TestBase):
    def setUp(self):
        super().setUp()
        self.professional_team_service = RiotProfessionalTeamService(self.db)

    def test_get_professional_teams_by_slug_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters(slug=expected_team.slug)

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_slug_no_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters(slug="badSlug")

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_name_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters(name=expected_team.name)

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_name_no_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters(name="badName")

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_code_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters(code=expected_team.code)

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_code_no_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters(code="badCode")

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_status_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters(status=expected_team.status)

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_status_no_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters(status="badStatus")

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_home_league_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters(league=expected_team.home_league_name)

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_home_league_no_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters(league="badLeague")

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_empty_query_string_params(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)
        search_parameters = TeamSearchParameters()

        # Act
        professional_team_from_db = self.professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_team_by_id(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)

        # Act
        professional_team_from_db = self.professional_team_service.get_team_by_id(expected_team.id)

        # Assert
        self.assertEqual(professional_team_from_db, expected_team)

    def test_get_professional_team_by_id_invalid_id(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)

        # Act and Assert
        with self.assertRaises(ProfessionalTeamNotFoundException):
            self.professional_team_service.get_team_by_id(ProTeamID("777"))

    def test_search_matches_name_case_insensitive(self):
        self.db.put_team(riot_fixtures.team_1_fixture)
        partial = riot_fixtures.team_1_fixture.name[:4].lower()
        params = TeamSearchParameters(search=partial)

        result = self.professional_team_service.get_teams(params)

        self.assertEqual(1, len(result))
        self.assertEqual(riot_fixtures.team_1_fixture.id, result[0].id)

    def test_search_matches_code_case_insensitive(self):
        self.db.put_team(riot_fixtures.team_1_fixture)
        params = TeamSearchParameters(search=riot_fixtures.team_1_fixture.code.lower())

        result = self.professional_team_service.get_teams(params)

        self.assertEqual(1, len(result))
        self.assertEqual(riot_fixtures.team_1_fixture.id, result[0].id)

    def test_search_no_match(self):
        self.db.put_team(riot_fixtures.team_1_fixture)
        params = TeamSearchParameters(search="zzzzz")

        result = self.professional_team_service.get_teams(params)

        self.assertEqual(0, len(result))

    def test_fantasy_available_filter(self):
        self.db.put_league(riot_fixtures.league_1_fixture)  # fantasy_available=False
        self.db.put_league(riot_fixtures.league_2_fixture)  # fantasy_available=True
        team_in_fantasy = riot_fixtures.team_1_fixture.model_copy(deep=True)
        team_in_fantasy.home_league_name = riot_fixtures.league_2_fixture.name
        self.db.put_team(team_in_fantasy)
        team_not_in_fantasy = riot_fixtures.team_2_fixture.model_copy(deep=True)
        team_not_in_fantasy.home_league_name = riot_fixtures.league_1_fixture.name
        self.db.put_team(team_not_in_fantasy)

        params = TeamSearchParameters(fantasy_available=True)
        result = self.professional_team_service.get_teams(params)

        team_ids = [t.id for t in result]
        self.assertIn(team_in_fantasy.id, team_ids)
        self.assertNotIn(team_not_in_fantasy.id, team_ids)

    def test_active_only_excludes_archived(self):
        from src.common.schemas.riot_data_schemas import ProfessionalTeam

        archived_team = ProfessionalTeam(
            id=ProTeamID("archived-team-test"),
            slug="archived",
            name="Archived",
            code="ARC",
            image="http://arc.png",
            status="archived",
        )
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(archived_team)

        params = TeamSearchParameters(active_only=True)
        result = self.professional_team_service.get_teams(params)

        team_ids = [t.id for t in result]
        self.assertIn(riot_fixtures.team_1_fixture.id, team_ids)
        self.assertNotIn(archived_team.id, team_ids)

    def test_active_only_false_includes_archived(self):
        from src.common.schemas.riot_data_schemas import ProfessionalTeam

        archived_team = ProfessionalTeam(
            id=ProTeamID("archived-team-test-2"),
            slug="archived2",
            name="Archived2",
            code="AR2",
            image="http://ar2.png",
            status="archived",
        )
        self.db.put_team(archived_team)

        params = TeamSearchParameters(active_only=False)
        result = self.professional_team_service.get_teams(params)

        team_ids = [t.id for t in result]
        self.assertIn(archived_team.id, team_ids)

    def test_has_players_excludes_teams_without_players(self):
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)
        # Only add a player to team_1
        self.db.put_player(riot_fixtures.player_1_fixture)

        params = TeamSearchParameters(has_players=True)
        result = self.professional_team_service.get_teams(params)

        team_ids = [t.id for t in result]
        self.assertIn(riot_fixtures.team_1_fixture.id, team_ids)
        self.assertNotIn(riot_fixtures.team_2_fixture.id, team_ids)

    def test_has_players_none_returns_all(self):
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)

        params = TeamSearchParameters(has_players=None)
        result = self.professional_team_service.get_teams(params)

        self.assertEqual(2, len(result))
