from fastapi.testclient import TestClient
from http import HTTPStatus
from unittest.mock import patch

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.riot_api_requester_util import RiotApiRequestUtil
from fantasylol.exceptions.league_not_found_exception import LeagueNotFoundException
from fantasylol.schemas.riot_data_schemas import LeagueSchema
from fantasylol import app

LEAGUE_BASE_URL = "/riot/v1/league"
BASE_LEAGUE_SERVICE_MOCK_PATH = "fantasylol.service.riot_league_service.RiotLeagueService"
GET_LEAGUES_MOCK_PATH = f"{BASE_LEAGUE_SERVICE_MOCK_PATH}.get_leagues"
GET_LEAGUE_BY_ID_MOCK_PATH = f"{BASE_LEAGUE_SERVICE_MOCK_PATH}.get_league_by_id"


class LeagueEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        riot_api_util = RiotApiRequestUtil()
        self.league_db_fixture = riot_api_util.create_mock_league()
        self.expected_league_response_schema = LeagueSchema(**self.league_db_fixture.to_dict())
        self.client = TestClient(app)

    @patch(GET_LEAGUES_MOCK_PATH)
    def test_get_leagues_endpoint_search_all(self, mock_get_leagues):
        # Arrange
        mock_get_leagues.return_value = [self.league_db_fixture]

        # Act
        response = self.client.get(LEAGUE_BASE_URL)

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(1, len(leagues))
        league_response_schema = LeagueSchema(**leagues[0])
        self.assertEqual(self.expected_league_response_schema, league_response_schema)
        mock_get_leagues.assert_called_once_with({
            "name": None,
            "region": None
        })

    @patch(GET_LEAGUES_MOCK_PATH)
    def test_get_leagues_endpoint_name_filter_existing_league(self, mock_get_leagues):
        # Arrange
        mock_get_leagues.return_value = [self.league_db_fixture]

        # Act
        response = self.client.get(
            f"{LEAGUE_BASE_URL}?name={self.league_db_fixture.name}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(1, len(leagues))
        league_response_schema = LeagueSchema(**leagues[0])
        self.assertEqual(self.expected_league_response_schema, league_response_schema)
        mock_get_leagues.assert_called_once_with({
            "name": self.league_db_fixture.name,
            "region": None
        })

    @patch(GET_LEAGUES_MOCK_PATH)
    def test_get_leagues_endpoint_region_filter_existing_league(self, mock_get_leagues):
        # Arrange
        mock_get_leagues.return_value = [self.league_db_fixture]

        # Act
        response = self.client.get(
            f"{LEAGUE_BASE_URL}?region={self.league_db_fixture.region}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(1, len(leagues))
        league_response_schema = LeagueSchema(**leagues[0])
        self.assertEqual(self.expected_league_response_schema, league_response_schema)
        mock_get_leagues.assert_called_once_with({
            "name": None,
            "region": self.league_db_fixture.region
        })

    @patch(GET_LEAGUE_BY_ID_MOCK_PATH)
    def test_get_league_by_id_endpoint_successful(self, mock_get_league_by_id):
        # Arrange
        mock_get_league_by_id.return_value = self.league_db_fixture

        # Act
        response = self.client.get(f"{LEAGUE_BASE_URL}/{self.league_db_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        league = response.json()
        self.assertIsInstance(league, dict)
        league_response_schema = LeagueSchema(**league)
        self.assertEqual(self.expected_league_response_schema, league_response_schema)
        mock_get_league_by_id.assert_called_once_with(self.league_db_fixture.id)

    @patch(GET_LEAGUE_BY_ID_MOCK_PATH)
    def test_get_league_by_id_endpoint_not_found(self, mock_get_league_by_id):
        # Arrange
        mock_get_league_by_id.side_effect = LeagueNotFoundException

        # Act
        response = self.client.get(f"{LEAGUE_BASE_URL}/{self.league_db_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_league_by_id.assert_called_once_with(self.league_db_fixture.id)
