from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from http import HTTPStatus
from unittest.mock import patch

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import test_fixtures as fixtures

from fantasylol.exceptions.league_not_found_exception import LeagueNotFoundException
from fantasylol.schemas.search_parameters import LeagueSearchParameters
from fantasylol import app

LEAGUE_BASE_URL = "/riot/v1/league"
BASE_LEAGUE_SERVICE_MOCK_PATH = "fantasylol.service.riot_league_service.RiotLeagueService"
GET_LEAGUES_MOCK_PATH = f"{BASE_LEAGUE_SERVICE_MOCK_PATH}.get_leagues"
GET_LEAGUE_BY_ID_MOCK_PATH = f"{BASE_LEAGUE_SERVICE_MOCK_PATH}.get_league_by_id"


class LeagueEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        add_pagination(app)
        self.client = TestClient(app)

    @patch(GET_LEAGUES_MOCK_PATH)
    def test_get_leagues_endpoint_search_all(self, mock_get_leagues):
        # Arrange
        league_fixture = fixtures.league_fixture
        expected_league_response = league_fixture.model_dump()
        mock_get_leagues.return_value = [league_fixture]

        # Act
        response = self.client.get(LEAGUE_BASE_URL)

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        leagues = response_json.get('items')
        self.assertIsInstance(leagues, list)
        self.assertEqual(1, len(leagues))
        self.assertEqual(expected_league_response, leagues[0])
        mock_get_leagues.assert_called_once_with(LeagueSearchParameters())

    @patch(GET_LEAGUES_MOCK_PATH)
    def test_get_leagues_endpoint_name_filter_existing_league(self, mock_get_leagues):
        # Arrange
        league_fixture = fixtures.league_fixture
        expected_league_response = league_fixture.model_dump()
        mock_get_leagues.return_value = [league_fixture]

        # Act
        response = self.client.get(
            f"{LEAGUE_BASE_URL}?name={league_fixture.name}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        leagues = response_json.get('items')
        self.assertIsInstance(leagues, list)
        self.assertEqual(1, len(leagues))
        self.assertEqual(expected_league_response, leagues[0])
        mock_get_leagues.assert_called_once_with(
            LeagueSearchParameters(name=league_fixture.name)
        )

    @patch(GET_LEAGUES_MOCK_PATH)
    def test_get_leagues_endpoint_region_filter_existing_league(self, mock_get_leagues):
        # Arrange
        league_fixture = fixtures.league_fixture
        expected_league_response = league_fixture.model_dump()
        mock_get_leagues.return_value = [league_fixture]

        # Act
        response = self.client.get(
            f"{LEAGUE_BASE_URL}?region={league_fixture.region}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        leagues = response_json.get('items')
        self.assertIsInstance(leagues, list)
        self.assertEqual(1, len(leagues))
        self.assertEqual(expected_league_response, leagues[0])
        mock_get_leagues.assert_called_once_with(
            LeagueSearchParameters(region=league_fixture.region)
        )

    @patch(GET_LEAGUE_BY_ID_MOCK_PATH)
    def test_get_league_by_id_endpoint_successful(self, mock_get_league_by_id):
        # Arrange
        league_fixture = fixtures.league_fixture
        expected_league_response = league_fixture.model_dump()
        mock_get_league_by_id.return_value = league_fixture

        # Act
        response = self.client.get(f"{LEAGUE_BASE_URL}/{league_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        league = response.json()
        self.assertIsInstance(league, dict)
        self.assertEqual(expected_league_response, league)
        mock_get_league_by_id.assert_called_once_with(league_fixture.id)

    @patch(GET_LEAGUE_BY_ID_MOCK_PATH)
    def test_get_league_by_id_endpoint_not_found(self, mock_get_league_by_id):
        # Arrange
        league_fixture = fixtures.league_fixture
        mock_get_league_by_id.side_effect = LeagueNotFoundException

        # Act
        response = self.client.get(f"{LEAGUE_BASE_URL}/{league_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_league_by_id.assert_called_once_with(league_fixture.id)
