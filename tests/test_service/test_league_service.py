from http import HTTPStatus
from unittest.mock import Mock, patch

from tests.fantasy_lol_test_base import FantasyLolTestBase, RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from tests.riot_api_requester_util import RiotApiRequestUtil
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import League
from fantasylol.exceptions.riot_api_status_code_assert_exception import \
    RiotApiStatusCodeAssertException
from fantasylol.exceptions.league_not_found_exception import LeagueNotFoundException
from fantasylol.service.riot_league_service import RiotLeagueService


class LeagueServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()

    def create_league_service(self):
        return RiotLeagueService()

    def create_league_in_db(self):
        mock_league = self.riot_api_util.create_mock_league()
        with DatabaseConnection() as db:
            db.add(mock_league)
            db.commit()
            db.refresh(mock_league)
        return mock_league

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_leagues_successful(self, mock_create_scraper):
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
    def test_fetch_leagues_fail(self, mock_create_scraper):

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        league_service = self.create_league_service()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            league_service.fetch_and_store_leagues()

    def test_get_leagues_by_name_existing_league(self):
        expected_league = self.create_league_in_db()
        query_params = {"name": expected_league.name}

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues(query_params)
        self.assertIsInstance(league_from_db, list)
        self.assertEqual(len(league_from_db), 1)
        self.assertEqual(league_from_db[0], expected_league)

    def test_get_leagues_by_name_no_existing_league(self):
        self.create_league_in_db()
        query_params = {"name": "badName"}

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues(query_params)
        self.assertIsInstance(league_from_db, list)
        self.assertEqual(len(league_from_db), 0)

    def test_get_leagues_by_region_existing_league(self):
        expected_league = self.create_league_in_db()
        query_params = {"region": expected_league.region}

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues(query_params)
        self.assertIsInstance(league_from_db, list)
        self.assertEqual(len(league_from_db), 1)
        self.assertEqual(league_from_db[0], expected_league)

    def test_get_leagues_by_region_no_existing_league(self):
        self.create_league_in_db()
        query_params = {"region": "badRegion"}

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues(query_params)
        self.assertIsInstance(league_from_db, list)
        self.assertEqual(len(league_from_db), 0)

    def test_get_leagues_no_query_params(self):
        expected_league = self.create_league_in_db()

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues()
        self.assertIsInstance(league_from_db, list)
        self.assertEqual(len(league_from_db), 1)
        self.assertEqual(league_from_db[0], expected_league)

    def test_get_leagues_empty_query_params(self):
        expected_league = self.create_league_in_db()
        query_params = {}

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues(query_params)
        self.assertIsInstance(league_from_db, list)
        self.assertEqual(len(league_from_db), 1)
        self.assertEqual(league_from_db[0], expected_league)

    def test_get_league_by_id_valid_id(self):
        expected_league = self.create_league_in_db()
        league_service = self.create_league_service()
        league_from_db = league_service.get_league_by_id(expected_league.id)
        self.assertEqual(league_from_db, expected_league)

    def test_get_league_by_id_invalid_id(self):
        self.create_league_in_db()
        league_service = self.create_league_service()
        with self.assertRaises(LeagueNotFoundException):
            league_service.get_league_by_id(777)
