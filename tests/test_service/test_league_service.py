from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.riot_api_requester_util import RiotApiRequestUtil

from fantasylol.db.database import DatabaseConnection
from fantasylol.exceptions.league_not_found_exception import LeagueNotFoundException
from fantasylol.service.riot_league_service import RiotLeagueService
from fantasylol.schemas.search_parameters import LeagueSearchParameters


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

    def test_get_leagues_by_name_existing_league(self):
        expected_league = self.create_league_in_db()
        search_parameters = LeagueSearchParameters(name=expected_league.name)

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues(search_parameters)
        self.assertIsInstance(league_from_db, list)
        self.assertEqual(len(league_from_db), 1)
        self.assertEqual(league_from_db[0], expected_league)

    def test_get_leagues_by_name_no_existing_league(self):
        self.create_league_in_db()
        search_parameters = LeagueSearchParameters(name="badName")

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues(search_parameters)
        self.assertIsInstance(league_from_db, list)
        self.assertEqual(len(league_from_db), 0)

    def test_get_leagues_by_region_existing_league(self):
        expected_league = self.create_league_in_db()
        search_parameters = LeagueSearchParameters(region=expected_league.region)

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues(search_parameters)
        self.assertIsInstance(league_from_db, list)
        self.assertEqual(len(league_from_db), 1)
        self.assertEqual(league_from_db[0], expected_league)

    def test_get_leagues_by_region_no_existing_league(self):
        self.create_league_in_db()
        search_parameters = LeagueSearchParameters(region="badRegion")

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues(search_parameters)
        self.assertIsInstance(league_from_db, list)
        self.assertEqual(len(league_from_db), 0)

    def test_get_leagues_empty_query_params(self):
        expected_league = self.create_league_in_db()

        league_service = self.create_league_service()
        league_from_db = league_service.get_leagues(LeagueSearchParameters())
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
