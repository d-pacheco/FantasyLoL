from http import HTTPStatus
from unittest.mock import Mock, patch

from riot.util.riot_api_requester import RiotApiRequester
from riot.exceptions.riot_api_status_code_assert_exception import \
    RiotApiStatusCodeAssertException

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import riot_api_requester_util
from tests.test_util import test_fixtures

RIOT_API_REQUESTER_CLOUDSCRAPER_PATH = \
    'riot.util.riot_api_requester.cloudscraper.create_scraper'

RIOT_API_REQUESTER_GET_TOURNAMENT_ID_FOR_MATCH_PATH = \
    'riot.util.riot_api_requester.RiotApiRequester.get_tournament_id_for_match'


class RiotApiRequesterTest(FantasyLolTestBase):

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_leagues_successful(self, mock_cloud_scraper):
        # Arrange
        expected_league = test_fixtures.league_1_fixture

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = riot_api_requester_util.get_leagues_mock_response
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        leagues = riot_api_requester.get_leagues()

        # Assert
        self.assertIsInstance(leagues, list)
        self.assertEqual(1, len(leagues))
        self.assertEqual(expected_league, leagues[0])

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_leagues_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_leagues()

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_tournaments_for_league_successful(self, mock_cloud_scraper):
        # Arrange
        expected_tournament = test_fixtures.tournament_fixture

        expected_json = riot_api_requester_util.get_tournaments_for_league_response
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        tournaments = riot_api_requester.get_tournament_for_league(expected_tournament.league_id)

        # Assert
        self.assertIsInstance(tournaments, list)
        self.assertEqual(1, len(tournaments))
        self.assertEqual(expected_tournament, tournaments[0])

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_tournaments_for_league_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client
        league_fixture = test_fixtures.league_1_fixture

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_tournament_for_league(league_fixture.id)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_teams_successful(self, mock_cloud_scraper):
        # Arrange
        expected_tournament = test_fixtures.tournament_fixture

        expected_json = riot_api_requester_util.get_tournaments_for_league_response
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        tournaments = riot_api_requester.get_tournament_for_league(expected_tournament.league_id)

        # Assert
        self.assertIsInstance(tournaments, list)
        self.assertEqual(1, len(tournaments))
        self.assertEqual(expected_tournament, tournaments[0])

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_teams_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_teams()

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_players_successful(self, mock_cloud_scraper):
        # Arrange
        expected_players = [
            test_fixtures.player_1_fixture,
            test_fixtures.player_2_fixture,
            test_fixtures.player_3_fixture,
            test_fixtures.player_4_fixture,
            test_fixtures.player_5_fixture
        ]

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = riot_api_requester_util.get_teams_response
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        players = riot_api_requester.get_players()

        # Assert
        self.assertIsInstance(players, list)
        self.assertEqual(5, len(players))

        self.assertEqual(expected_players[0], players[0])
        self.assertEqual(expected_players[1], players[1])
        self.assertEqual(expected_players[2], players[2])
        self.assertEqual(expected_players[3], players[3])
        self.assertEqual(expected_players[4], players[4])

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_players_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_players()

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_games_from_event_details_successful(self, mock_cloud_scraper):
        # Arrange
        expected_games = [
            test_fixtures.game_1_fixture_completed,
            test_fixtures.game_2_fixture_inprogress,
            test_fixtures.game_3_fixture_unstarted
        ]

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = riot_api_requester_util.get_event_details_response
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        match_fixture = test_fixtures.match_fixture
        riot_api_requester = RiotApiRequester()
        games = riot_api_requester.get_games_from_event_details(match_fixture.id)

        # Assert
        self.assertIsInstance(games, list)
        self.assertEqual(3, len(games))
        self.assertEqual(expected_games[0], games[0])
        self.assertEqual(expected_games[1], games[1])
        self.assertEqual(expected_games[2], games[2])

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_games_from_event_details_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        match_fixture = test_fixtures.match_fixture
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_games_from_event_details(match_fixture.id)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_games_from_event_details_no_content_status_code(self, mock_cloud_scraper):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.NO_CONTENT
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        match_fixture = test_fixtures.match_fixture
        riot_api_requester = RiotApiRequester()
        games = riot_api_requester.get_games_from_event_details(match_fixture.id)

        # Assert
        self.assertIsInstance(games, list)
        self.assertEqual(0, len(games))

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_games_successful(self, mock_cloud_scraper):
        # Arrange
        expected_get_games_response = test_fixtures.get_games_response_game_1_fixture
        game_ids_to_get = [test_fixtures.game_1_fixture_completed.id]

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = riot_api_requester_util.get_games_response
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        get_games_responses = riot_api_requester.get_games(game_ids_to_get)

        # Assert
        self.assertIsInstance(get_games_responses, list)
        self.assertEqual(1, len(get_games_responses))
        self.assertEqual(expected_get_games_response, get_games_responses[0])

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_games_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        game_ids_to_get = [test_fixtures.game_1_fixture_completed.id]

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_games(game_ids_to_get)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_player_metadata_for_game_successful(self, mock_cloud_scraper):
        # Arrange
        game = test_fixtures.game_1_fixture_completed
        time_stamp = "randomTimeStamp"
        expected_player_metadata = [
            test_fixtures.player_1_game_metadata_fixture,
            test_fixtures.player_2_game_metadata_fixture,
            test_fixtures.player_3_game_metadata_fixture,
            test_fixtures.player_4_game_metadata_fixture,
            test_fixtures.player_5_game_metadata_fixture,
            test_fixtures.player_6_game_metadata_fixture,
            test_fixtures.player_7_game_metadata_fixture,
            test_fixtures.player_8_game_metadata_fixture,
            test_fixtures.player_9_game_metadata_fixture,
            test_fixtures.player_10_game_metadata_fixture
        ]

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = riot_api_requester_util.get_livestats_window_response
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        get_player_metadata_response = riot_api_requester\
            .get_player_metadata_for_game(game.id, time_stamp)

        # Assert
        self.assertIsInstance(get_player_metadata_response, list)
        self.assertEqual(10, len(get_player_metadata_response))
        self.assertEqual(expected_player_metadata[0], get_player_metadata_response[0])
        self.assertEqual(expected_player_metadata[1], get_player_metadata_response[1])
        self.assertEqual(expected_player_metadata[2], get_player_metadata_response[2])
        self.assertEqual(expected_player_metadata[3], get_player_metadata_response[3])
        self.assertEqual(expected_player_metadata[4], get_player_metadata_response[4])
        self.assertEqual(expected_player_metadata[5], get_player_metadata_response[5])
        self.assertEqual(expected_player_metadata[6], get_player_metadata_response[6])
        self.assertEqual(expected_player_metadata[7], get_player_metadata_response[7])
        self.assertEqual(expected_player_metadata[8], get_player_metadata_response[8])
        self.assertEqual(expected_player_metadata[9], get_player_metadata_response[9])

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_player_metadata_for_game_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        game = test_fixtures.game_1_fixture_completed
        time_stamp = "randomTimeStamp"

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_player_metadata_for_game(game.id, time_stamp)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_player_metadata_for_game_no_content_status_code(self, mock_cloud_scraper):
        # Arrange
        game = test_fixtures.game_1_fixture_completed
        time_stamp = "randomTimeStamp"

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.NO_CONTENT
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        get_player_metadata_response = riot_api_requester\
            .get_player_metadata_for_game(game.id, time_stamp)

        # Assert
        self.assertIsInstance(get_player_metadata_response, list)
        self.assertEqual(0, len(get_player_metadata_response))

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_player_stats_for_game_successful(self, mock_cloud_scraper):
        # Arrange
        game = test_fixtures.game_1_fixture_completed
        time_stamp = "randomTimeStamp"
        expected_player_stats = [
            test_fixtures.player_1_game_stats_fixture,
            test_fixtures.player_2_game_stats_fixture,
            test_fixtures.player_3_game_stats_fixture,
            test_fixtures.player_4_game_stats_fixture,
            test_fixtures.player_5_game_stats_fixture,
            test_fixtures.player_6_game_stats_fixture,
            test_fixtures.player_7_game_stats_fixture,
            test_fixtures.player_8_game_stats_fixture,
            test_fixtures.player_9_game_stats_fixture,
            test_fixtures.player_10_game_stats_fixture,
        ]

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = riot_api_requester_util.get_live_stats_details_response
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        get_player_stats_response = riot_api_requester \
            .get_player_stats_for_game(game.id, time_stamp)

        # Assert
        self.assertIsInstance(get_player_stats_response, list)
        self.assertEqual(10, len(get_player_stats_response))
        self.assertEqual(expected_player_stats[0], get_player_stats_response[0])
        self.assertEqual(expected_player_stats[1], get_player_stats_response[1])
        self.assertEqual(expected_player_stats[2], get_player_stats_response[2])
        self.assertEqual(expected_player_stats[3], get_player_stats_response[3])
        self.assertEqual(expected_player_stats[4], get_player_stats_response[4])
        self.assertEqual(expected_player_stats[5], get_player_stats_response[5])
        self.assertEqual(expected_player_stats[6], get_player_stats_response[6])
        self.assertEqual(expected_player_stats[7], get_player_stats_response[7])
        self.assertEqual(expected_player_stats[8], get_player_stats_response[8])
        self.assertEqual(expected_player_stats[9], get_player_stats_response[9])

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_player_stats_for_game_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        game = test_fixtures.game_1_fixture_completed
        time_stamp = "randomTimeStamp"

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_player_stats_for_game(game.id, time_stamp)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_player_stats_for_game_no_content_status_code(self, mock_cloud_scraper):
        # Arrange
        game = test_fixtures.game_1_fixture_completed
        time_stamp = "randomTimeStamp"

        mock_response = Mock()
        mock_response.status_code = HTTPStatus.NO_CONTENT
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        get_player_stats_response = riot_api_requester \
            .get_player_stats_for_game(game.id, time_stamp)

        # Assert
        self.assertIsInstance(get_player_stats_response, list)
        self.assertEqual(0, len(get_player_stats_response))

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_player_stats_for_game_empty_frames_in_response(self, mock_cloud_scraper):
        # Arrange
        game = test_fixtures.game_1_fixture_completed
        time_stamp = "randomTimeStamp"

        expected_json = riot_api_requester_util.get_live_stats_details_empty_frames_response
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        get_player_stats_response = riot_api_requester \
            .get_player_stats_for_game(game.id, time_stamp)

        # Assert
        self.assertIsInstance(get_player_stats_response, list)
        self.assertEqual(0, len(get_player_stats_response))

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_tournament_id_for_match_successful(self, mock_cloud_scraper):
        # Arrange
        expected_tournament_id = test_fixtures.tournament_fixture.id
        match = test_fixtures.match_fixture
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = riot_api_requester_util.get_event_details_response
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        tournament_id = riot_api_requester.get_tournament_id_for_match(match.id)

        # Assert
        self.assertIsInstance(tournament_id, str)
        self.assertEqual(expected_tournament_id, tournament_id)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_tournament_id_for_match_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        match = test_fixtures.match_fixture
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.NO_CONTENT
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_tournament_id_for_match(match.id)

    @patch(RIOT_API_REQUESTER_GET_TOURNAMENT_ID_FOR_MATCH_PATH)
    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_matches_from_schedule_successful(
            self, mock_cloud_scraper, mock_get_tournament_id_for_match):
        # Arrange
        expected_match = test_fixtures.match_fixture
        mock_get_tournament_id_for_match.return_value = test_fixtures.tournament_fixture.id
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = riot_api_requester_util.get_schedule_response
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        matches = riot_api_requester.get_matches_from_schedule()

        # Assert
        self.assertIsInstance(matches, list)
        self.assertEqual(1, len(matches))
        self.assertEqual(expected_match, matches[0])

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_matches_from_schedule_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.NO_CONTENT
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_matches_from_schedule()

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_pages_from_schedule_successful(self, mock_cloud_scraper):
        # Arrange
        expected_page_tokens = test_fixtures.riot_schedule_pages_fixture
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = riot_api_requester_util.get_schedule_response
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act
        riot_api_requester = RiotApiRequester()
        pages = riot_api_requester.get_pages_from_schedule()

        # Assert
        self.assertEqual(expected_page_tokens, pages)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_pages_from_schedule_status_code_assertion(self, mock_cloud_scraper):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.NO_CONTENT
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        # Act and Assert
        riot_api_requester = RiotApiRequester()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            riot_api_requester.get_pages_from_schedule()
