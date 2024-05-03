from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from unittest.mock import patch
from http import HTTPStatus

from tests.test_base import FantasyLolTestBase
from tests.test_util import riot_fixtures as fixtures

from src.riot.exceptions.professional_team_not_found_exception import \
    ProfessionalTeamNotFoundException
from src.common.schemas.search_parameters import TeamSearchParameters
from src.riot import app

PROFESSIONAL_TEAM_BASE_URL = "/riot/v1/professional-team"
BASE_TEAM_SERVICE_MOCK_PATH = \
    "src.riot.service.riot_professional_team_service.RiotProfessionalTeamService"
TEAM_SERVICE_GET_TEAMS_MOCK_PATH = f"{BASE_TEAM_SERVICE_MOCK_PATH}.get_teams"
TEAM_SERVICE_GET_TEAM_BY_ID_MOCK_PATH = f"{BASE_TEAM_SERVICE_MOCK_PATH}.get_team_by_id"


class ProfessionalTeamEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        add_pagination(app)
        self.client = TestClient(app)

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_slug_query(self, mock_get_teams):
        # Arrange
        team_fixture = fixtures.team_1_fixture
        expected_team_response = team_fixture.model_dump()
        mock_get_teams.return_value = [team_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_TEAM_BASE_URL}?slug={team_fixture.slug}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        professional_teams = response_json.get('items')
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        self.assertEqual(expected_team_response, professional_teams[0])
        mock_get_teams.assert_called_once_with(
            TeamSearchParameters(slug=team_fixture.slug)
        )

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_name_query(self, mock_get_teams):
        # Arrange
        team_fixture = fixtures.team_1_fixture
        expected_team_response = team_fixture.model_dump()
        mock_get_teams.return_value = [team_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_TEAM_BASE_URL}?name={team_fixture.name}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        professional_teams = response_json.get('items')
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        self.assertEqual(expected_team_response, professional_teams[0])
        mock_get_teams.assert_called_once_with(
            TeamSearchParameters(name=team_fixture.name)
        )

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_code_query(self, mock_get_teams):
        # Arrange
        team_fixture = fixtures.team_1_fixture
        expected_team_response = team_fixture.model_dump()
        mock_get_teams.return_value = [team_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_TEAM_BASE_URL}?code={team_fixture.code}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        professional_teams = response_json.get('items')
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        self.assertEqual(expected_team_response, professional_teams[0])
        mock_get_teams.assert_called_once_with(
            TeamSearchParameters(code=team_fixture.code)
        )

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_status_query(self, mock_get_teams):
        # Arrange
        team_fixture = fixtures.team_1_fixture
        expected_team_response = team_fixture.model_dump()
        mock_get_teams.return_value = [team_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_TEAM_BASE_URL}?status={team_fixture.status}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        professional_teams = response_json.get('items')
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        self.assertEqual(expected_team_response, professional_teams[0])
        mock_get_teams.assert_called_once_with(
            TeamSearchParameters(status=team_fixture.status)
        )

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_league_query(self, mock_get_teams):
        # Arrange
        team_fixture = fixtures.team_1_fixture
        expected_team_response = team_fixture.model_dump()
        mock_get_teams.return_value = [team_fixture]

        # Act
        response = self.client.get(
            f"{PROFESSIONAL_TEAM_BASE_URL}?league={team_fixture.home_league}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        professional_teams = response_json.get('items')
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        self.assertEqual(expected_team_response, professional_teams[0])
        mock_get_teams.assert_called_once_with(
            TeamSearchParameters(league=team_fixture.home_league)
        )

    @patch(TEAM_SERVICE_GET_TEAMS_MOCK_PATH)
    def test_get_professional_teams_endpoint_search_all(self, mock_get_teams):
        # Arrange
        team_fixture = fixtures.team_1_fixture
        expected_team_response = team_fixture.model_dump()
        mock_get_teams.return_value = [team_fixture]

        # Act
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        professional_teams = response_json.get('items')
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(1, len(professional_teams))
        self.assertEqual(expected_team_response, professional_teams[0])
        mock_get_teams.assert_called_once_with(TeamSearchParameters())

    @patch(TEAM_SERVICE_GET_TEAM_BY_ID_MOCK_PATH)
    def test_get_professional_team_by_id_success(self, mock_get_team_by_id):
        # Arrange
        team_fixture = fixtures.team_1_fixture
        expected_team_response = team_fixture.model_dump()
        mock_get_team_by_id.return_value = team_fixture

        # Act
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}/{team_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        professional_team = response.json()
        self.assertIsInstance(professional_team, dict)
        self.assertEqual(expected_team_response, professional_team)
        mock_get_team_by_id.assert_called_once_with(team_fixture.id)

    @patch(TEAM_SERVICE_GET_TEAM_BY_ID_MOCK_PATH)
    def test_get_professional_team_by_id_not_found(self, mock_get_team_by_id):
        # Arrange
        team_fixture = fixtures.team_1_fixture
        mock_get_team_by_id.side_effect = ProfessionalTeamNotFoundException

        # Act
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}/{team_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_team_by_id.assert_called_once_with(team_fixture.id)
