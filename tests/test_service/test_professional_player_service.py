import uuid
from http import HTTPStatus
from unittest.mock import Mock, patch
from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.fantasy_lol_test_base import RIOT_API_REQUESTER_CLOUDSCRAPER_PATH
from tests.riot_api_requester_util import RiotApiRequestUtil

from fantasylol.db.database import DatabaseConnection
from fantasylol.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from fantasylol.exceptions.riot_api_status_code_assert_exception import \
    RiotApiStatusCodeAssertException
from fantasylol.db.models import ProfessionalPlayer
from fantasylol.service.riot_professional_player_service import RiotProfessionalPlayerService


def create_professional_player_service():
    return RiotProfessionalPlayerService()


class ProfessionalPlayerServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()

    def create_professional_player_and_team_in_db(self):
        mock_player = self.riot_api_util.create_mock_player()
        mock_team = self.riot_api_util.create_mock_team()
        with DatabaseConnection() as db:
            db.add(mock_team)
            db.commit()
            db.add(mock_player)
            db.commit()
            db.refresh(mock_team)
            db.refresh(mock_player)
        return mock_player, mock_team

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_professional_player_successful(self, mock_api_requester):
        expected_json = self.riot_api_util.create_mock_team_response()

        # Configure the mock api requester to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = expected_json
        mock_client.get.return_value = mock_response
        mock_api_requester.return_value = mock_client

        professional_player_service = create_professional_player_service()
        professional_player_service.fetch_and_store_professional_players()

        with DatabaseConnection() as db:
            players_from_db = db.query(ProfessionalPlayer).all()
        self.assertEqual(5, len(players_from_db))

    @patch(RIOT_API_REQUESTER_CLOUDSCRAPER_PATH)
    def test_fetch_professional_player_fail(self, mock_create_scraper):

        # Configure the mock client to return the mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_client.get.return_value = mock_response
        mock_create_scraper.return_value = mock_client

        professional_player_service = create_professional_player_service()
        with self.assertRaises(RiotApiStatusCodeAssertException):
            professional_player_service.fetch_and_store_professional_players()

    def test_get_existing_professional_players_by_summoner_name(self):
        expected_player, expected_team = self.create_professional_player_and_team_in_db()
        query_params = {"summoner_name": expected_player.summoner_name}

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(query_params)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_summoner_name(self):
        self.create_professional_player_and_team_in_db()
        query_params = {"summoner_name": "badSummonerName"}

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(query_params)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_existing_professional_players_by_role(self):
        expected_player, expected_team = self.create_professional_player_and_team_in_db()
        query_params = {"role": expected_player.role}

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(query_params)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_role(self):
        self.create_professional_player_and_team_in_db()
        query_params = {"role": "badRole"}

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(query_params)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_existing_professional_players_by_team_id(self):
        expected_player, expected_team = self.create_professional_player_and_team_in_db()
        query_params = {"team_id": expected_player.team_id}

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(query_params)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_team_id(self):
        self.create_professional_player_and_team_in_db()
        query_params = {"team_id": 777}

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(query_params)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_professional_player_by_id(self):
        expected_player, expected_team = self.create_professional_player_and_team_in_db()
        professional_player_service = create_professional_player_service()
        player_from_db = professional_player_service.get_player_by_id(expected_player.id)
        self.assertEqual(player_from_db, expected_player)

    def test_get_professional_player_by_id_invalid_id(self):
        self.create_professional_player_and_team_in_db()
        professional_player_service = create_professional_player_service()
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            professional_player_service.get_player_by_id(str(uuid.uuid4()))
