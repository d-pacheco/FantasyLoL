from http import HTTPStatus
from unittest.mock import Mock, patch

from tests.FantasyLolTestBase import FantasyLolTestBase, RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from tests.RiotApiRequesterUtil import RiotApiRequestUtil
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import League
from fantasylol.exceptions.RiotApiStatusException import RiotApiStatusCodeAssertException
from fantasylol.service.RiotLeagueService import RiotLeagueService


class LeagueServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()

    def create_league_service(self):
        return RiotLeagueService()
    
    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_leagues_successful(self, mock_create_scraper):
        expected_json = self.riot_api_util.create_mock_league_response()
        expected_league = self.riot_api_util.create_mock_league()

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        league_service = self.create_league_service()
        league_service.fetch_and_store_leagues()

        with DatabaseConnection() as db:
            league_from_db = db.query(League).filter_by(id=expected_league.id).first()
        self.assertEqual(league_from_db, expected_league)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_leagues_fail(self, mock_create_scraper):

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        league_service = self.create_league_service()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            league_service.fetch_and_store_leagues()
