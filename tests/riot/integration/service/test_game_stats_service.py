from http import HTTPStatus
from unittest.mock import Mock, patch

from tests.test_base import TestBase, RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from tests.test_util import riot_api_requester_util, riot_fixtures

from src.riot.service import RiotGameStatsService


class GameStatsServiceTest(TestBase):

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_player_metadata_for_game_successful(self, mock_cloud_scraper):
        # Arrange
        game = riot_fixtures.game_1_fixture_completed
        expected_json = riot_api_requester_util.get_livestats_window_response

        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        game_stats_service = RiotGameStatsService(self.db)

        # Act
        game_stats_service.fetch_and_store_player_metadata_for_game(game.id)

        # Assert
        self.assertEqual(game.id, expected_json['esportsGameId'])
        player_metadata_from_db = self.test_db.get_all_game_metadata()
        self.assertEqual(10, len(player_metadata_from_db))
