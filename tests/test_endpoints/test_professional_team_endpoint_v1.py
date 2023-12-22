from fastapi.testclient import TestClient
from unittest.mock import patch
from http import HTTPStatus

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.riot_api_requester_util import RiotApiRequestUtil
from fantasylol.exceptions.professional_team_not_found_exception import \
    ProfessionalTeamNotFoundException
from fantasylol.schemas.riot_data_schemas import ProfessionalTeamSchema
from fantasylol import app

PROFESSIONAL_TEAM_BASE_URL = "/riot/v1/professional-team"
BASE_TEAM_SERVICE_MOCK_PATH = \
    "fantasylol.service.riot_professional_team_service.RiotProfessionalTeamService"
TEAM_SERVICE_GET_TEAMS_MOCK_PATH = f"{BASE_TEAM_SERVICE_MOCK_PATH}.get_teams"
TEAM_SERVICE_GET_TEAM_BY_ID_MOCK_PATH = f"{BASE_TEAM_SERVICE_MOCK_PATH}.get_team_by_id"


def create_team_query_params(
        slug: str = None,
        name: str = None,
        code: str = None,
        status: str = None,
        league: str = None):
    return {
        "slug": slug,
        "name": name,
        "code": code,
        "status": status,
        "home_league": league
    }


class ProfessionalTeamEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        self.client = TestClient(app)
        self.riot_api_util = RiotApiRequestUtil()

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_slug_query(self, mock_get_teams):
        # Arrange
        team_db_fixture = self.riot_api_util.create_mock_team()
        expected_team_response_schema = ProfessionalTeamSchema(**team_db_fixture.to_dict())
        mock_get_teams.return_value = [team_db_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_TEAM_BASE_URL}?slug={team_db_fixture.slug}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        team_response_schema_from_request = ProfessionalTeamSchema(**professional_teams[0])
        self.assertEqual(expected_team_response_schema, team_response_schema_from_request)
        mock_get_teams.assert_called_once_with(
            create_team_query_params(slug=team_db_fixture.slug)
        )

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_name_query(self, mock_get_teams):
        # Arrange
        team_db_fixture = self.riot_api_util.create_mock_team()
        expected_team_response_schema = ProfessionalTeamSchema(**team_db_fixture.to_dict())
        mock_get_teams.return_value = [team_db_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_TEAM_BASE_URL}?name={team_db_fixture.name}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        team_response_schema_from_request = ProfessionalTeamSchema(**professional_teams[0])
        self.assertEqual(expected_team_response_schema, team_response_schema_from_request)
        mock_get_teams.assert_called_once_with(
            create_team_query_params(name=team_db_fixture.name)
        )

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_code_query(self, mock_get_teams):
        # Arrange
        team_db_fixture = self.riot_api_util.create_mock_team()
        expected_team_response_schema = ProfessionalTeamSchema(**team_db_fixture.to_dict())
        mock_get_teams.return_value = [team_db_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_TEAM_BASE_URL}?code={team_db_fixture.code}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        team_response_schema_from_request = ProfessionalTeamSchema(**professional_teams[0])
        self.assertEqual(expected_team_response_schema, team_response_schema_from_request)
        mock_get_teams.assert_called_once_with(
            create_team_query_params(code=team_db_fixture.code)
        )

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_status_query(self, mock_get_teams):
        # Arrange
        team_db_fixture = self.riot_api_util.create_mock_team()
        expected_team_response_schema = ProfessionalTeamSchema(**team_db_fixture.to_dict())
        mock_get_teams.return_value = [team_db_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_TEAM_BASE_URL}?status={team_db_fixture.status}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        team_response_schema_from_request = ProfessionalTeamSchema(**professional_teams[0])
        self.assertEqual(expected_team_response_schema, team_response_schema_from_request)
        mock_get_teams.assert_called_once_with(
            create_team_query_params(status=team_db_fixture.status)
        )

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_league_query(self, mock_get_teams):
        # Arrange
        team_db_fixture = self.riot_api_util.create_mock_team()
        expected_team_response_schema = ProfessionalTeamSchema(**team_db_fixture.to_dict())
        mock_get_teams.return_value = [team_db_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_TEAM_BASE_URL}?league={team_db_fixture.home_league}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        team_response_schema_from_request = ProfessionalTeamSchema(**professional_teams[0])
        self.assertEqual(expected_team_response_schema, team_response_schema_from_request)
        mock_get_teams.assert_called_once_with(
            create_team_query_params(league=team_db_fixture.home_league)
        )

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_search_all(self, mock_get_teams):
        # Arrange
        team_db_fixture = self.riot_api_util.create_mock_team()
        expected_team_response_schema = ProfessionalTeamSchema(**team_db_fixture.to_dict())
        mock_get_teams.return_value = [team_db_fixture]

        # Act
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        team_response_schema_from_request = ProfessionalTeamSchema(**professional_teams[0])
        self.assertEqual(expected_team_response_schema, team_response_schema_from_request)
        mock_get_teams.assert_called_once_with(create_team_query_params())

    @patch(TEAM_SERVICE_GET_TEAM_BY_ID_MOCK_PATH)
    def test_get_professional_team_by_id_success(self, mock_get_team_by_id):
        # Arrange
        team_db_fixture = self.riot_api_util.create_mock_team()
        expected_team_response_schema = ProfessionalTeamSchema(**team_db_fixture.to_dict())
        mock_get_team_by_id.return_value = team_db_fixture

        # Act
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}/{team_db_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        professional_team = response.json()
        self.assertIsInstance(professional_team, dict)
        team_response_schema_from_request = ProfessionalTeamSchema(**professional_team)
        self.assertEqual(expected_team_response_schema, team_response_schema_from_request)
        mock_get_team_by_id.assert_called_once_with(team_db_fixture.id)

    @patch(TEAM_SERVICE_GET_TEAM_BY_ID_MOCK_PATH)
    def test_get_professional_team_by_id_not_found(self, mock_get_team_by_id):
        # Arrange
        team_db_fixture = self.riot_api_util.create_mock_team()
        mock_get_team_by_id.side_effect = ProfessionalTeamNotFoundException

        # Act
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}/{team_db_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_team_by_id.assert_called_once_with(team_db_fixture.id)
