from http import HTTPStatus
from unittest.mock import Mock, patch

from .FantasyLolTestBase import FantasyLolTestBase, RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from .RiotApiRequesterUtil import RiotApiRequestUtil
from db.database import DatabaseConnection
from db.models import Tournament
from db.models import League
from exceptions.RiotApiStatusException import RiotApiStatusCodeAssertException
from service.RiotTournamentService import RiotTournamentService


class TournamentServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()
        mock_league = self.riot_api_util.create_mock_league()
        with DatabaseConnection() as db:
            db.add(mock_league)
            db.commit()

    def create_tournament_service(self):
        return RiotTournamentService()
    
    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_tournaments_successful(self, mock_create_scraper):
        expected_json = self.riot_api_util.create_mock_tournament_response()
        expected_tournament = self.riot_api_util.create_mock_tournament()

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        tournament_service = self.create_tournament_service()
        tournament_service.fetch_and_store_tournaments()
        with DatabaseConnection() as db:
            tournament_from_db = db.query(Tournament).filter_by(id=expected_tournament.id).first()
        self.assertEqual(tournament_from_db, expected_tournament)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_tournaments_status_code_error(self, mock_create_scraper):

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        tournament_service = self.create_tournament_service()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            tournament_service.fetch_and_store_tournaments()
