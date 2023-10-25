from http import HTTPStatus
from unittest.mock import Mock, patch

from .FantasyLolTestBase import FantasyLolTestBase, RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from .RiotApiRequesterUtil import RiotApiRequestUtil
from db.database import DatabaseConnection
from db.models import ProfessionalTeam
from exceptions.RiotApiStatusException import RiotApiStatusCodeAssertException
from service.RiotProfessionalTeamService import RiotProfessionalTeamService


class ProfessionalTeamServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()

    def create_professional_team_service(self):
        return RiotProfessionalTeamService()
    
    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_professional_team_successful(self, mock_create_scraper):
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
    def test_get_leagues_fail(self, mock_create_scraper):

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        professional_team_service = self.create_professional_team_service()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            professional_team_service.fetch_and_store_professional_teams()
