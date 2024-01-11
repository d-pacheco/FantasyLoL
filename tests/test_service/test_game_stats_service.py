from http import HTTPStatus
from unittest.mock import Mock, patch

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.fantasy_lol_test_base import RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from tests.riot_api_requester_util import RiotApiRequestUtil

from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import PlayerGameMetadata
from fantasylol.service.riot_game_stats_service import RiotGameStatsService


def create_game_stats_service():
    return RiotGameStatsService()


class GameStatsServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_player_metadata_for_game_successful(self, mock_cloud_scraper):
        expected_json = self.riot_api_util.create_mock_window_response()

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        game_stats_service = create_game_stats_service()
        game_stats_service.fetch_and_store_player_metadata_for_game(
            int(self.riot_api_util.mock_game_1_id)
        )

        with DatabaseConnection() as db:
            player_metadata_from_db = db.query(PlayerGameMetadata).all()
        self.assertEqual(10, len(player_metadata_from_db))
