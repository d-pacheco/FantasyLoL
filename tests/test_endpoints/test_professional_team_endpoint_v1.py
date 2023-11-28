from fastapi.testclient import TestClient
from http import HTTPStatus

from tests.FantasyLolTestBase import FantasyLolTestBase
from tests.RiotApiRequesterUtil import RiotApiRequestUtil
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import ProfessionalTeam
from fantasylol import app


PROFESSIONAL_TEAM_BASE_URL = "/riot/v1/professional-team"

class ProfessionalTeamEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        self.client = TestClient(app)
        self.riot_api_util = RiotApiRequestUtil()

    def create_professional_team_in_db(self):
        mock_team = self.riot_api_util.create_mock_team()
        with DatabaseConnection() as db:
            db.add(mock_team)
            db.commit()
            db.refresh(mock_team)
        return mock_team
    
    def test_get_professional_teams_endpoint_slug_query(self):
        expected_professional_team = self.create_professional_team_in_db()
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}?slug={expected_professional_team.slug}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(len(professional_teams), 1)

        professional_teams_from_request = ProfessionalTeam(**professional_teams[0])
        self.assertEqual(professional_teams_from_request, expected_professional_team)

    def test_get_professional_teams_endpoint_name_query(self):
        expected_professional_team = self.create_professional_team_in_db()
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}?name={expected_professional_team.name}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(len(professional_teams), 1)

        professional_teams_from_request = ProfessionalTeam(**professional_teams[0])
        self.assertEqual(professional_teams_from_request, expected_professional_team)

    def test_get_professional_teams_endpoint_code_query(self):
        expected_professional_team = self.create_professional_team_in_db()
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}?code={expected_professional_team.code}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(len(professional_teams), 1)

        professional_teams_from_request = ProfessionalTeam(**professional_teams[0])
        self.assertEqual(professional_teams_from_request, expected_professional_team)

    def test_get_professional_teams_endpoint_status_query(self):
        expected_professional_team = self.create_professional_team_in_db()
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}?status={expected_professional_team.status}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(len(professional_teams), 1)

        professional_teams_from_request = ProfessionalTeam(**professional_teams[0])
        self.assertEqual(professional_teams_from_request, expected_professional_team)

    def test_get_professional_teams_endpoint_league_query(self):
        expected_professional_team = self.create_professional_team_in_db()
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}?league={expected_professional_team.home_league}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(len(professional_teams), 1)

        professional_teams_from_request = ProfessionalTeam(**professional_teams[0])
        self.assertEqual(professional_teams_from_request, expected_professional_team)

    def test_get_professional_teams_endpoint_all_leagues(self):
        self.create_professional_team_in_db()
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        professional_teams = response.json()
        self.assertIsInstance(professional_teams, list)
        self.assertEqual(len(professional_teams), 1)

    def test_get_professional_team_by_id_success(self):
        expected_professional_team = self.create_professional_team_in_db()
        professional_team_id = expected_professional_team.id
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}/{professional_team_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        professional_team = response.json()
        self.assertIsInstance(professional_team, dict)
        professional_team_from_request = ProfessionalTeam(**professional_team)
        self.assertEqual(professional_team_from_request, expected_professional_team)

    def test_get_professional_team_by_id_with_invalid_id(self):
        professional_team_id = 777
        response = self.client.get(f"{PROFESSIONAL_TEAM_BASE_URL}/{professional_team_id}")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response_msg = response.json()
        self.assertIn("Professional Team not found", response_msg['detail'])
    