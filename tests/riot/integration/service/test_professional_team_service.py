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
        search_parameters = TeamSearchParameters(league=expected_team.home_league)

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
