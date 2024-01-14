from fantasylol.db.database import DatabaseConnection
from fantasylol.exceptions.match_not_found_exception import MatchNotFoundException
from fantasylol.service.riot_match_service import RiotMatchService
from fantasylol.schemas.search_parameters import MatchSearchParameters

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.riot_api_requester_util import RiotApiRequestUtil


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

    def test_get_matches_by_league_slug_existing_match(self):
        expected_match = self.create_match_in_db()
        search_parameters = MatchSearchParameters(league_slug=expected_match.league_slug)

        match_service = self.create_match_service()
        matches_from_db = match_service.get_matches(search_parameters)
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        self.assertEqual(expected_match, matches_from_db[0])

    def test_get_matches_by_league_slug_no_existing_match(self):
        self.create_match_in_db()
        search_parameters = MatchSearchParameters(league_slug="bad-slug")

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
