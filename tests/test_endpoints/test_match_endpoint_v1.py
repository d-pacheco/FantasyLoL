from fastapi.testclient import TestClient
from http import HTTPStatus

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.riot_api_requester_util import RiotApiRequestUtil
from fantasylol.db.database import DatabaseConnection
from fantasylol import app


class MatchEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        self.client = TestClient(app)
        self.riot_api_util = RiotApiRequestUtil()
        self.match_in_db = self.create_match_in_db()

    def create_match_in_db(self):
        mock_match = self.riot_api_util.create_mock_match()
        with DatabaseConnection() as db:
            db.add(mock_match)
            db.commit()
            db.refresh(mock_match)
        return mock_match

    def test_get_riot_matches(self):
        expected_match_json = self.match_in_db.to_dict()
        response = self.client.get("riot/v1/matches")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        response_matches = response.json()
        self.assertIsInstance(response_matches, list)
        self.assertEqual(1, len(response_matches))
        self.assertEqual(expected_match_json, response_matches[0])

    def test_get_riot_matches_filter_by_league_name_returns_existing_matches(self):
        expected_match_json = self.match_in_db.to_dict()
        league_name = self.match_in_db.league_name
        response = self.client.get(f"riot/v1/matches?league_name={league_name}")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        response_matches = response.json()
        self.assertIsInstance(response_matches, list)
        self.assertEqual(1, len(response_matches))
        self.assertEqual(expected_match_json, response_matches[0])

    def test_get_riot_matches_filter_by_league_name_returns_empty_list_when_no_matches_match(self):
        response = self.client.get("riot/v1/matches?league_name=badName")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        response_matches = response.json()
        self.assertIsInstance(response_matches, list)
        self.assertEqual(0, len(response_matches))

    def test_get_riot_matches_filter_by_tournament_id_returns_existing_matches(self):
        expected_match_json = self.match_in_db.to_dict()
        tournament_id = self.match_in_db.tournament_id
        response = self.client.get(f"riot/v1/matches?tournament_id={tournament_id}")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        response_matches = response.json()
        self.assertIsInstance(response_matches, list)
        self.assertEqual(1, len(response_matches))
        self.assertEqual(expected_match_json, response_matches[0])

    def test_get_riot_matches_filter_tournament_id_returns_empty_list_when_no_matches_match(self):
        response = self.client.get("riot/v1/matches?tournament_id=777")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        response_matches = response.json()
        self.assertIsInstance(response_matches, list)
        self.assertEqual(0, len(response_matches))

    def test_get_matches_correct_league_name_and_bad_tournament_id_filters_return_empty_list(self):
        league_name = self.match_in_db.league_name
        tournament_id = 777
        request_url = f"riot/v1/matches?league_name={league_name}&tournament_id={tournament_id}"
        response = self.client.get(request_url)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        response_matches = response.json()
        self.assertIsInstance(response_matches, list)
        self.assertEqual(0, len(response_matches))

    def test_get_matches_bad_league_name_and_correct_tournament_id_filters_return_empty_list(self):
        league_name = "badName"
        tournament_id = self.match_in_db.tournament_id
        request_url = f"riot/v1/matches?league_name={league_name}&tournament_id={tournament_id}"
        response = self.client.get(request_url)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        response_matches = response.json()
        self.assertIsInstance(response_matches, list)
        self.assertEqual(0, len(response_matches))

    def test_get_matches_correct_league_name_and_tournament_id_filters_return_expected_match(self):
        league_name = self.match_in_db.league_name
        tournament_id = self.match_in_db.tournament_id
        request_url = f"riot/v1/matches?league_name={league_name}&tournament_id={tournament_id}"
        response = self.client.get(request_url)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        expected_match_json = self.match_in_db.to_dict()
        response_matches = response.json()
        self.assertIsInstance(response_matches, list)
        self.assertEqual(1, len(response_matches))
        self.assertEqual(expected_match_json, response_matches[0])

    def test_get_matches_by_id_for_existing_match_returns_expected_match(self):
        expected_match_json = self.match_in_db.to_dict()
        match_id = self.match_in_db.id
        response = self.client.get(f"riot/v1/matches/{match_id}")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        response_match = response.json()
        self.assertEqual(expected_match_json, response_match)

    def test_get_matches_by_id_for_no_existing_match_returns_not_found_response(self):
        response = self.client.get("riot/v1/matches/777")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        response_msg = response.json()
        self.assertEqual("Match not found", response_msg['detail'])
