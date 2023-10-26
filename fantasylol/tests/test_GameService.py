from http import HTTPStatus
from unittest.mock import Mock, patch

from .FantasyLolTestBase import FantasyLolTestBase, RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from .RiotApiRequesterUtil import RiotApiRequestUtil
from db.database import DatabaseConnection
from db.models import Game
from exceptions.RiotApiStatusException import RiotApiStatusCodeAssertException
from service.RiotGameService import RiotGameService


class GameServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()

    def create_game_service(self):
        return RiotGameService()
    
    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_live_games_successful(self, mock_create_scraper):
        expected_json = self.riot_api_util.create_mock_live_game_response()
        expected_game = self.riot_api_util.create_mock_game()

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        game_service = self.create_game_service()
        game_service.fetch_and_store_live_games()

        with DatabaseConnection() as db:
            game_from_db = db.query(Game).filter_by(id=expected_game.id).first()
        self.assertEqual(game_from_db, expected_game)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_state_of_game_fail(self, mock_create_scraper):

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        # Create an instance of RiotApiService and call the method to test
        game_service = self.create_game_service()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            game_service.fetch_and_store_live_games()
