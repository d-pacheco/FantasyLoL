from http import HTTPStatus
from unittest.mock import Mock, patch

from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import Match
from fantasylol.exceptions.riot_api_status_code_assert_exception import \
    RiotApiStatusCodeAssertException
from fantasylol.exceptions.match_not_found_exception import MatchNotFoundException
from fantasylol.service.riot_match_service import RiotMatchService
from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.fantasy_lol_test_base import RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from tests.riot_api_requester_util import RiotApiRequestUtil
from fantasylol.schemas.search_parameters import MatchSearchParameters


class MatchServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()

    def create_match_service(self):
        return RiotMatchService()

    def create_match_in_db(self):
        mock_match = self.riot_api_util.create_mock_match()
        with DatabaseConnection() as db:
            db.add(mock_match)
            db.commit()
            db.refresh(mock_match)
        return mock_match

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_matches_for_tournament_successful(self, mock_cloud_scraper):
        expected_json = self.riot_api_util.create_mock_match_response()
        expected_match = self.riot_api_util.create_mock_match()

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        match_service = self.create_match_service()
        fetched_matches = match_service.fetch_and_store_matchs_from_tournament(
            self.riot_api_util.mock_tournament_id
        )
        self.assertIsInstance(fetched_matches, list)
        self.assertEqual(1, len(fetched_matches))
        self.assertEqual(expected_match.to_dict(), fetched_matches[0].to_dict())

        # assert that the matches were saved to the DB
        with DatabaseConnection() as db:
            match_from_db = db.query(Match) \
                .filter_by(id=expected_match.id).first()
        self.assertEqual(expected_match, match_from_db)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_matches_for_tournament_fail(self, mock_cloud_scraper):
        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client.get.return_value = mock_response
        mock_cloud_scraper.return_value = mock_client

        match_service = self.create_match_service()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            match_service.fetch_and_store_matchs_from_tournament(
                self.riot_api_util.mock_tournament_id
            )

    def test_get_matches_by_league_name_existing_match(self):
        expected_match = self.create_match_in_db()
        search_parameters = MatchSearchParameters(league_name=expected_match.league_name)

        match_service = self.create_match_service()
        matches_from_db = match_service.get_matches(search_parameters)
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        self.assertEqual(expected_match, matches_from_db[0])

    def test_get_matches_by_league_name_no_existing_match(self):
        self.create_match_in_db()
        search_parameters = MatchSearchParameters(league_name="badName")

        match_service = self.create_match_service()
        matches_from_db = match_service.get_matches(search_parameters)
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(0, len(matches_from_db))

    def test_get_matches_by_tournament_id_existing_match(self):
        expected_match = self.create_match_in_db()
        search_parameters = MatchSearchParameters(tournament_id=expected_match.tournament_id)

        match_service = self.create_match_service()
        matches_from_db = match_service.get_matches(search_parameters)
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        self.assertEqual(expected_match, matches_from_db[0])

    def test_get_matches_by_tournament_id_no_existing_match(self):
        self.create_match_in_db()
        search_parameters = MatchSearchParameters(tournament_id=777)

        match_service = self.create_match_service()
        matches_from_db = match_service.get_matches(search_parameters)
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(0, len(matches_from_db))

    def test_get_matches_with_empty_query_params(self):
        expected_match = self.create_match_in_db()

        match_service = self.create_match_service()
        matches_from_db = match_service.get_matches(MatchSearchParameters())
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        self.assertEqual(expected_match, matches_from_db[0])

    def test_get_matches_by_id_with_valid_id(self):
        expected_match = self.create_match_in_db()
        match_service = self.create_match_service()
        match_from_db = match_service.get_match_by_id(expected_match.id)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_by_id_with_invalid_id(self):
        self.create_match_in_db()
        match_service = self.create_match_service()
        with self.assertRaises(MatchNotFoundException):
            match_service.get_match_by_id(777)
