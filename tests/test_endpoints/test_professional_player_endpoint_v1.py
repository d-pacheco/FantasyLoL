from unittest.mock import patch
from fastapi.testclient import TestClient
from http import HTTPStatus

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.riot_api_requester_util import RiotApiRequestUtil
from fantasylol.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from fantasylol.schemas.riot_data_schemas import ProfessionalPlayerSchema
from fantasylol import app

PROFESSIONAL_PLAYER_BASE_URL = "/riot/v1/professional-player"
BASE_PLAYER_SERVICE_MOCK_PATH = \
    "fantasylol.service.riot_professional_player_service.RiotProfessionalPlayerService"
PLAYER_SERVICE_GET_PLAYERS_MOCK_PATH = f"{BASE_PLAYER_SERVICE_MOCK_PATH}.get_players"
PLAYER_SERVICE_GET_PLAYER_BY_ID_MOCK_PATH = f"{BASE_PLAYER_SERVICE_MOCK_PATH}.get_player_by_id"


class ProfessionalPlayerEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        self.client = TestClient(app)
        self.riot_api_util = RiotApiRequestUtil()

    @patch(PLAYER_SERVICE_GET_PLAYERS_MOCK_PATH)
    def test_get_professional_players_endpoint_summoner_name_query(self, mock_get_players):
        db_fixture = self.riot_api_util.create_mock_player()
        expected_player_response_schema = ProfessionalPlayerSchema(**db_fixture.to_dict())
        mock_get_players.return_value = [db_fixture]

        response = self.client.get(
            f"{PROFESSIONAL_PLAYER_BASE_URL}?summoner_name={db_fixture.summoner_name}"
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        professional_players = response.json()
        self.assertIsInstance(professional_players, list)
        self.assertEqual(1, len(professional_players))
        player_response_schema_from_request = ProfessionalPlayerSchema(**professional_players[0])
        self.assertEqual(expected_player_response_schema, player_response_schema_from_request)
        mock_get_players.assert_called_once_with({
            "summoner_name": db_fixture.summoner_name,
            "role": None,
            "team_id": None
        })

    @patch(PLAYER_SERVICE_GET_PLAYERS_MOCK_PATH)
    def test_get_professional_players_endpoint_role_query(self, mock_get_players):
        db_fixture = self.riot_api_util.create_mock_player()
        expected_player_response_schema = ProfessionalPlayerSchema(**db_fixture.to_dict())
        mock_get_players.return_value = [db_fixture]

        response = self.client.get(
            f"{PROFESSIONAL_PLAYER_BASE_URL}?role={db_fixture.role}"
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        professional_players = response.json()
        self.assertIsInstance(professional_players, list)
        self.assertEqual(1, len(professional_players))
        player_response_schema_from_request = ProfessionalPlayerSchema(**professional_players[0])
        self.assertEqual(expected_player_response_schema, player_response_schema_from_request)
        mock_get_players.assert_called_once_with({
            "summoner_name": None,
            "role": db_fixture.role,
            "team_id": None
        })

    @patch(PLAYER_SERVICE_GET_PLAYERS_MOCK_PATH)
    def test_get_professional_players_endpoint_team_id_query(self, mock_get_players):
        db_fixture = self.riot_api_util.create_mock_player()
        expected_player_response_schema = ProfessionalPlayerSchema(**db_fixture.to_dict())
        mock_get_players.return_value = [db_fixture]

        response = self.client.get(
            f"{PROFESSIONAL_PLAYER_BASE_URL}?team_id={db_fixture.team_id}"
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        professional_players = response.json()
        self.assertIsInstance(professional_players, list)
        self.assertEqual(1, len(professional_players))
        player_response_schema_from_request = ProfessionalPlayerSchema(**professional_players[0])
        self.assertEqual(expected_player_response_schema, player_response_schema_from_request)
        mock_get_players.assert_called_once_with({
            "summoner_name": None,
            "role": None,
            "team_id": db_fixture.team_id
        })

    @patch(PLAYER_SERVICE_GET_PLAYERS_MOCK_PATH)
    def test_get_professional_players_endpoint_search_all(self, mock_get_players):
        db_fixture = self.riot_api_util.create_mock_player()
        expected_player_response_schema = ProfessionalPlayerSchema(**db_fixture.to_dict())
        mock_get_players.return_value = [db_fixture]

        response = self.client.get(f"{PROFESSIONAL_PLAYER_BASE_URL}")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        professional_players = response.json()
        self.assertIsInstance(professional_players, list)
        self.assertEqual(1, len(professional_players))
        player_response_schema_from_request = ProfessionalPlayerSchema(**professional_players[0])
        self.assertEqual(expected_player_response_schema, player_response_schema_from_request)
        mock_get_players.assert_called_once_with({
            "summoner_name": None,
            "role": None,
            "team_id": None
        })

    @patch(PLAYER_SERVICE_GET_PLAYER_BY_ID_MOCK_PATH)
    def test_get_professional_players_endpoint_by_id(self, mock_get_player_by_id):
        db_fixture = self.riot_api_util.create_mock_player()
        expected_player_response_schema = ProfessionalPlayerSchema(**db_fixture.to_dict())
        mock_get_player_by_id.return_value = db_fixture

        response = self.client.get(f"{PROFESSIONAL_PLAYER_BASE_URL}/{db_fixture.id}")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        professional_player = response.json()
        self.assertIsInstance(professional_player, dict)
        player_response_schema_from_request = ProfessionalPlayerSchema(**professional_player)
        self.assertEqual(expected_player_response_schema, player_response_schema_from_request)
        mock_get_player_by_id.assert_called_once_with(db_fixture.id)

    @patch(PLAYER_SERVICE_GET_PLAYER_BY_ID_MOCK_PATH)
    def test_get_professional_players_endpoint_by_id_not_found(self, mock_get_player_by_id):
        db_fixture = self.riot_api_util.create_mock_player()
        mock_get_player_by_id.side_effect = ProfessionalPlayerNotFoundException

        response = self.client.get(f"{PROFESSIONAL_PLAYER_BASE_URL}/{db_fixture.id}")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_player_by_id.assert_called_once_with(db_fixture.id)
