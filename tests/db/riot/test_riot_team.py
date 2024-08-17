from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.schemas.riot_data_schemas import ProfessionalTeam
from src.db.models import ProfessionalTeamModel


class TestCrudRiotTeam(TestBase):
    def test_put_team_no_existing_team(self):
        # Arrange
        team = riot_fixtures.team_1_fixture

        # Act and Assert
        team_before_put = self.db.get_team_by_id(team.id)
        self.assertIsNone(team_before_put)
        self.db.put_team(team)
        team_after_put = self.db.get_team_by_id(team.id)
        self.assertEqual(team, team_after_put)

    def test_put_team_existing_team(self):
        # Arrange
        team = riot_fixtures.team_1_fixture
        self.db.put_team(team)
        updated_team = team.model_copy(deep=True)
        updated_team.status = "inactive"

        # Act and Assert
        team_before_put = self.db.get_team_by_id(team.id)
        self.assertEqual(team, team_before_put)
        self.assertEqual(team.id, updated_team.id)
        self.assertNotEqual(team.status, updated_team.status)
        self.db.put_team(updated_team)
        team_after_put = self.db.get_team_by_id(team.id)
        self.assertEqual(updated_team, team_after_put)

    def test_get_teams_no_filters(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)

        # Act
        teams_from_db = self.db.get_teams()

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
        self.db.put_team(expected_team)

        # Act
        teams_from_db = self.db.get_teams(filters)

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
        filters.append(ProfessionalTeamModel.name == expected_team.name)
        self.db.put_team(expected_team)
        self.db.put_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = self.db.get_teams(filters)

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
        filters.append(ProfessionalTeamModel.name == team_1.name)
        self.db.put_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = self.db.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(0, len(teams_from_db))

    def test_get_teams_slug_filter_existing_team(self):
        # Arrange
        filters = []
        expected_team = riot_fixtures.team_1_fixture
        filters.append(ProfessionalTeamModel.slug == expected_team.slug)
        self.db.put_team(expected_team)
        self.db.put_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = self.db.get_teams(filters)

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
        filters.append(ProfessionalTeamModel.slug == team_1.slug)
        self.db.put_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = self.db.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(0, len(teams_from_db))

    def test_get_teams_code_filter_existing_team(self):
        # Arrange
        filters = []
        expected_team = riot_fixtures.team_1_fixture
        filters.append(ProfessionalTeamModel.code == expected_team.code)
        self.db.put_team(expected_team)
        self.db.put_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = self.db.get_teams(filters)

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
        filters.append(ProfessionalTeamModel.code == team_1.code)
        self.db.put_team(riot_fixtures.team_2_fixture)

        # Act
        teams_from_db = self.db.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(0, len(teams_from_db))

    def test_get_teams_status_filter_existing_team(self):
        # Arrange
        filters = []
        expected_team = riot_fixtures.team_1_fixture
        filters.append(ProfessionalTeamModel.status == expected_team.status)
        self.db.put_team(expected_team)

        # Act
        teams_from_db = self.db.get_teams(filters)

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
        filters.append(ProfessionalTeamModel.status == team_1.status)

        # Act
        teams_from_db = self.db.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(0, len(teams_from_db))

    def test_get_teams_league_filter_existing_team(self):
        # Arrange
        filters = []
        expected_team = riot_fixtures.team_1_fixture
        filters.append(ProfessionalTeamModel.home_league == expected_team.home_league)
        self.db.put_team(expected_team)

        # Act
        teams_from_db = self.db.get_teams(filters)

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
        filters.append(ProfessionalTeamModel.home_league == team_1.home_league)

        # Act
        teams_from_db = self.db.get_teams(filters)

        # Assert
        self.assertIsInstance(teams_from_db, list)
        self.assertEqual(0, len(teams_from_db))

    def test_get_team_by_id_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture
        self.db.put_team(expected_team)

        # Act
        team_from_db = self.db.get_team_by_id(expected_team.id)

        # Assert
        self.assertIsNotNone(team_from_db)
        self.assertIsInstance(team_from_db, ProfessionalTeam)
        self.assertEqual(expected_team, team_from_db)

    def test_get_team_from_id_no_existing_team(self):
        # Arrange
        expected_team = riot_fixtures.team_1_fixture

        # Act
        team_from_db = self.db.get_team_by_id(expected_team.id)

        # Assert
        self.assertIsNone(team_from_db)
