from fastapi.testclient import TestClient
from http import HTTPStatus

from tests.FantasyLolTestBase import FantasyLolTestBase
from tests.RiotApiRequesterUtil import RiotApiRequestUtil
from tests.test_util.tournament_test_util import TournamentTestUtil
from db.database import DatabaseConnection
from db.models import Tournament
from util.tournament_status import TournamentStatus
from main import app

class TournamentEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        self.client = TestClient(app)
        self.riot_api_util = RiotApiRequestUtil()

    def test_get_tournaments_endpoint_active(self):
        expected_tournament = TournamentTestUtil.create_active_tournament()
        status = TournamentStatus.ACTIVE
        response = self.client.get(f"/riot/v1/tournament?status={status}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        tournaments = response.json()
        self.assertIsInstance(tournaments, list)
        self.assertEqual(len(tournaments), 1)

        tournament_from_request = Tournament(**tournaments[0])
        self.assertEqual(tournament_from_request, expected_tournament)

    def test_get_tournaments_endpoint_completed(self):
        expected_tournament = TournamentTestUtil.create_completed_tournament()
        status = TournamentStatus.COMPLETED
        response = self.client.get(f"/riot/v1/tournament?status={status}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        tournaments = response.json()
        self.assertIsInstance(tournaments, list)
        self.assertEqual(len(tournaments), 1)

        tournament_from_request = Tournament(**tournaments[0])
        self.assertEqual(tournament_from_request, expected_tournament)

    def test_get_tournaments_endpoint_upcoming(self):
        expected_tournament = TournamentTestUtil.create_upcoming_tournament()
        status = TournamentStatus.UPCOMING
        response = self.client.get(f"/riot/v1/tournament?status={status}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        tournaments = response.json()
        self.assertIsInstance(tournaments, list)
        self.assertEqual(len(tournaments), 1)

        tournament_from_request = Tournament(**tournaments[0])
        self.assertEqual(tournament_from_request, expected_tournament)

    def test_get_tournaments_endpoint_upcoming(self):
        status = "invalid"
        response = self.client.get(f"/riot/v1/tournament?status={status}")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        response_msg = response.json()
        self.assertIn("Invalid status value", response_msg['detail'])

    def test_get_tournament_by_id_success(self):
        expected_tournament = TournamentTestUtil.create_completed_tournament()
        tournament_id = expected_tournament.id
        response = self.client.get(f"/riot/v1/tournament/{tournament_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        tournament = response.json()
        self.assertIsInstance(tournament, dict)

        tournament_from_request = Tournament(**tournament)
        self.assertEqual(tournament_from_request, expected_tournament)

    def test_get_tournament_by_id_with_invalid_id(self):
        tournament_id = 123123123
        response = self.client.get(f"/riot/v1/tournament/{tournament_id}")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response_msg = response.json()
        self.assertIn("Tournament not found", response_msg['detail'])
