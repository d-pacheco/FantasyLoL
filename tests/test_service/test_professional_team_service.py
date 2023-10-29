from http import HTTPStatus
from unittest.mock import Mock, patch

from tests.FantasyLolTestBase import FantasyLolTestBase, RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from tests.RiotApiRequesterUtil import RiotApiRequestUtil
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import ProfessionalTeam
from fantasylol.exceptions.RiotApiStatusException import RiotApiStatusCodeAssertException
from fantasylol.exceptions.ProfessionalTeamNotFoundException import ProfessionalTeamNotFoundException
from fantasylol.service.RiotProfessionalTeamService import RiotProfessionalTeamService


class ProfessionalTeamServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()

    def create_professional_team_service(self):
        return RiotProfessionalTeamService()
    
    def create_professional_team_in_db(self):
        mock_team = self.riot_api_util.create_mock_team()
        with DatabaseConnection() as db:
            db.add(mock_team)
            db.commit()
            db.refresh(mock_team)
        return mock_team
    
    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_professional_team_successful(self, mock_create_scraper):
        expected_json = self.riot_api_util.create_mock_team_response()
        expected_team = self.riot_api_util.create_mock_team()

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        professional_team_service = self.create_professional_team_service()
        professional_team_service.fetch_and_store_professional_teams()

        with DatabaseConnection() as db:
            team_from_db = db.query(ProfessionalTeam).filter_by(id=expected_team.id).first()
        self.assertEqual(team_from_db, expected_team)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_professional_team_fail(self, mock_create_scraper):

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        professional_team_service = self.create_professional_team_service()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            professional_team_service.fetch_and_store_professional_teams()

    def test_get_professional_teams_by_slug_existing_team(self):
        expected_team = self.create_professional_team_in_db()
        query_params = {"slug": expected_team.slug}

        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_slug_no_existing_team(self):
        self.create_professional_team_in_db()
        query_params = {"slug": "badSlug"}

        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_name_existing_team(self):
        expected_team = self.create_professional_team_in_db()
        query_params = {"name": expected_team.name}

        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_name_no_existing_team(self):
        self.create_professional_team_in_db()
        query_params = {"name": "badName"}

        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_code_existing_team(self):
        expected_team = self.create_professional_team_in_db()
        query_params = {"code": expected_team.code}

        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_code_no_existing_team(self):
        self.create_professional_team_in_db()
        query_params = {"slug": "badCode"}

        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_status_existing_team(self):
        expected_team = self.create_professional_team_in_db()
        query_params = {"status": expected_team.status}

        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_status_no_existing_team(self):
        self.create_professional_team_in_db()
        query_params = {"status": "badStatus"}

        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_by_home_league_existing_team(self):
        expected_team = self.create_professional_team_in_db()
        query_params = {"home_league": expected_team.home_league}

        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_by_home_league_no_existing_team(self):
        self.create_professional_team_in_db()
        query_params = {"home_league": "badHomeLeague"}

        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 0)

    def test_get_professional_teams_no_query_string_params(self):
        expected_team = self.create_professional_team_in_db()
        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams()
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_teams_empty_query_string_params(self):
        expected_team = self.create_professional_team_in_db()
        query_params = {}
        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_teams(query_params)
        self.assertIsInstance(professional_team_from_db, list)
        self.assertEqual(len(professional_team_from_db), 1)
        self.assertEqual(professional_team_from_db[0], expected_team)

    def test_get_professional_team_by_id(self):
        expected_team = self.create_professional_team_in_db()
        professional_team_service = self.create_professional_team_service()
        professional_team_from_db = professional_team_service.get_team_by_id(expected_team.id)
        self.assertEqual(professional_team_from_db, expected_team)

    def test_get_professional_team_by_id_invalid_id(self):
        self.create_professional_team_in_db()
        professional_team_service = self.create_professional_team_service()
        with self.assertRaises(ProfessionalTeamNotFoundException):
            professional_team_service.get_team_by_id(777)
