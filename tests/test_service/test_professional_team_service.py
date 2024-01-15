from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import riot_data_util

from fantasylol.exceptions.professional_team_not_found_exception import \
    ProfessionalTeamNotFoundException
from fantasylol.service.riot_professional_team_service import RiotProfessionalTeamService
from fantasylol.schemas.search_parameters import TeamSearchParameters


def create_professional_team_service():
    return RiotProfessionalTeamService()


class ProfessionalTeamServiceTest(FantasyLolTestBase):
    def test_get_professional_teams_by_slug_existing_team(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters(slug=expected_team.slug)

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_slug_no_existing_team(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters(slug="badSlug")

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_name_existing_team(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters(name=expected_team.name)

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_name_no_existing_team(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters(name="badName")

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_code_existing_team(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters(code=expected_team.code)

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_code_no_existing_team(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters(code="badCode")

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_status_existing_team(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters(status=expected_team.status)

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_status_no_existing_team(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters(status="badStatus")

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_home_league_existing_team(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters(league=expected_team.home_league)

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_home_league_no_existing_team(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters(league="badLeague")

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_empty_query_string_params(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()
        search_parameters = TeamSearchParameters()

        # Act
        professional_team_from_db = professional_team_service.get_teams(search_parameters)

        # Assert
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_team_by_id(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        expected_team = riot_data_util.create_professional_team_in_db()

        # Act
        professional_team_from_db = professional_team_service.get_team_by_id(expected_team.id)

        # Assert
        self.assertEqual(professional_team_from_db, expected_team)

    def test_get_professional_team_by_id_invalid_id(self):
        # Arrange
        professional_team_service = create_professional_team_service()
        riot_data_util.create_professional_team_in_db()

        # Act and Assert
        with self.assertRaises(ProfessionalTeamNotFoundException):
            professional_team_service.get_team_by_id("777")
