import datetime
from http import HTTPStatus
from unittest.mock import Mock, patch
import random

from tests.FantasyLolTestBase import FantasyLolTestBase, RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from tests.RiotApiRequesterUtil import RiotApiRequestUtil
from tests.test_util.tournament_test_util import TournamentTestUtil
from db.database import DatabaseConnection
from db.models import Tournament
from exceptions.RiotApiStatusException import RiotApiStatusCodeAssertException
from exceptions.TournamentNotFoundException import TournamentNotFoundException
from service.RiotTournamentService import RiotTournamentService
from util.tournament_status import TournamentStatus


class TournamentServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()
        mock_league = self.riot_api_util.create_mock_league()
        with DatabaseConnection() as db:
            db.add(mock_league)
            db.commit()

    def create_tournament_service(self):
        return RiotTournamentService()
    
    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_tournaments_successful(self, mock_create_scraper):
        expected_json = self.riot_api_util.create_mock_tournament_response()
        expected_tournament = self.riot_api_util.create_mock_tournament()

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        tournament_service = self.create_tournament_service()
        tournament_service.fetch_and_store_tournaments()
        with DatabaseConnection() as db:
            tournament_from_db = db.query(Tournament).filter_by(id=expected_tournament.id).first()
        self.assertEqual(tournament_from_db, expected_tournament)

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_get_tournaments_status_code_error(self, mock_create_scraper):

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        tournament_service = self.create_tournament_service()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            tournament_service.fetch_and_store_tournaments()

    def test_get_active_tournaments(self):
        TournamentTestUtil.create_completed_tournament()
        TournamentTestUtil.create_upcoming_tournament()
        expected_tournament = TournamentTestUtil.create_active_tournament()
        tournament_service = self.create_tournament_service()
        tournament_from_db = tournament_service.get_tournaments(TournamentStatus.ACTIVE)
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 1)
        self.assertEqual(tournament_from_db[0], expected_tournament)

    def test_get_active_tournaments_with_no_active_tournaments(self):
        TournamentTestUtil.create_completed_tournament()
        TournamentTestUtil.create_upcoming_tournament()
        tournament_service = self.create_tournament_service()
        tournament_from_db = tournament_service.get_tournaments(TournamentStatus.ACTIVE)
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 0)

    def test_get_completed_tournaments(self):
        TournamentTestUtil.create_active_tournament()
        TournamentTestUtil.create_upcoming_tournament()
        expected_tournament = TournamentTestUtil.create_completed_tournament()
        tournament_service = self.create_tournament_service()
        tournament_from_db = tournament_service.get_tournaments(TournamentStatus.COMPLETED)
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 1)
        self.assertEqual(tournament_from_db[0], expected_tournament)

    def test_get_completed_tournaments_with_no_completed_tournaments(self):
        TournamentTestUtil.create_active_tournament()
        TournamentTestUtil.create_upcoming_tournament()
        tournament_service = self.create_tournament_service()
        tournament_from_db = tournament_service.get_tournaments(TournamentStatus.COMPLETED)
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 0)

    def test_get_upcoming_tournaments(self):
        TournamentTestUtil.create_active_tournament()
        TournamentTestUtil.create_completed_tournament()
        expected_tournament = TournamentTestUtil.create_upcoming_tournament()
        tournament_service = self.create_tournament_service()
        tournament_from_db = tournament_service.get_tournaments(TournamentStatus.UPCOMING)
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 1)
        self.assertEqual(tournament_from_db[0], expected_tournament)

    def test_get_upcoming_tournaments_with_no_upcoming_tournaments(self):
        TournamentTestUtil.create_active_tournament()
        TournamentTestUtil.create_completed_tournament()
        tournament_service = self.create_tournament_service()
        tournament_from_db = tournament_service.get_tournaments(TournamentStatus.UPCOMING)
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 0)

    def test_get_all_tournaments(self):
        TournamentTestUtil.create_active_tournament()
        TournamentTestUtil.create_upcoming_tournament()
        TournamentTestUtil.create_completed_tournament()
        tournament_service = self.create_tournament_service()
        tournament_from_db = tournament_service.get_tournaments()
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 3)

    def test_get_tournament_by_id(self):
        TournamentTestUtil.create_upcoming_tournament()
        TournamentTestUtil.create_completed_tournament()
        expected_tournament = TournamentTestUtil.create_active_tournament()
        tournament_service = self.create_tournament_service()
        tournament_from_db = tournament_service.get_tournament_by_id(expected_tournament.id)
        self.assertEqual(tournament_from_db, expected_tournament)

    def test_get_tournament_by_id_invalid_id(self):
        TournamentTestUtil.create_active_tournament()
        tournament_service = self.create_tournament_service()
        with self.assertRaises(TournamentNotFoundException):
            tournament_service.get_tournament_by_id(777)
