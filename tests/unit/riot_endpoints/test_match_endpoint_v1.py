from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from http import HTTPStatus
from unittest.mock import patch

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import test_fixtures as fixtures

from fantasylol.exceptions.match_not_found_exception import MatchNotFoundException
from fantasylol.schemas.search_parameters import MatchSearchParameters
from fantasylol import app

MATCH_ENDPOINT_BASE_URL = "/riot/v1/matches"
BASE_MATCH_SERVICE_MOCK_PATH = "fantasylol.service.riot_match_service.RiotMatchService"
GET_MATCHES_MOCK_PATH = f"{BASE_MATCH_SERVICE_MOCK_PATH}.get_matches"
GET_MATCHES_BY_ID_MOCK_PATH = f"{BASE_MATCH_SERVICE_MOCK_PATH}.get_match_by_id"


class MatchEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        add_pagination(app)
        self.client = TestClient(app)

    @patch(GET_MATCHES_MOCK_PATH)
    def test_get_riot_matches_endpoint_search_all(self, mock_get_matches):
        # Arrange
        match_fixture = fixtures.match_fixture
        expected_match_response = match_fixture.model_dump()
        mock_get_matches.return_value = [match_fixture]

        # Act
        response = self.client.get(MATCH_ENDPOINT_BASE_URL)

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        response_matches = response_json.get('items')
        self.assertIsInstance(response_matches, list)
        self.assertEqual(1, len(response_matches))
        self.assertEqual(expected_match_response, response_matches[0])
        mock_get_matches.assert_called_once_with(MatchSearchParameters())

    @patch(GET_MATCHES_MOCK_PATH)
    def test_get_riot_matches_endpoint_filter_by_league_slug(self, mock_get_matches):
        # Arrange
        match_fixture = fixtures.match_fixture
        expected_match_response = match_fixture.model_dump()
        mock_get_matches.return_value = [match_fixture]

        # Act
        response = self.client.get(
            f"{MATCH_ENDPOINT_BASE_URL}?league_slug={match_fixture.league_slug}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        response_matches = response_json.get('items')
        self.assertIsInstance(response_matches, list)
        self.assertEqual(1, len(response_matches))
        self.assertEqual(expected_match_response, response_matches[0])
        mock_get_matches.assert_called_once_with(
            MatchSearchParameters(league_slug=match_fixture.league_slug)
        )

    @patch(GET_MATCHES_MOCK_PATH)
    def test_get_riot_matches_endpoint_filter_by_tournament_id(self, mock_get_matches):
        # Arrange
        match_fixture = fixtures.match_fixture
        expected_match_response = match_fixture.model_dump()
        mock_get_matches.return_value = [match_fixture]

        # Act
        response = self.client.get(
            f"{MATCH_ENDPOINT_BASE_URL}?tournament_id={match_fixture.tournament_id}"
        )

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_json: dict = response.json()
        response_matches = response_json.get('items')
        self.assertIsInstance(response_matches, list)
        self.assertEqual(1, len(response_matches))
        self.assertEqual(expected_match_response, response_matches[0])
        mock_get_matches.assert_called_once_with(
            MatchSearchParameters(tournament_id=match_fixture.tournament_id)
        )

    @patch(GET_MATCHES_BY_ID_MOCK_PATH)
    def test_get_matches_by_id_endpoint_for_existing_match(self, mock_get_match_by_id):
        # Arrange
        match_fixture = fixtures.match_fixture
        expected_match_response = match_fixture.model_dump()
        mock_get_match_by_id.return_value = match_fixture

        # Act
        response = self.client.get(f"{MATCH_ENDPOINT_BASE_URL}/{match_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.OK, response.status_code)
        response_match = response.json()
        self.assertIsInstance(response_match, dict)
        self.assertEqual(expected_match_response, response_match)
        mock_get_match_by_id.assert_called_once_with(match_fixture.id)

    @patch(GET_MATCHES_BY_ID_MOCK_PATH)
    def test_get_matches_by_id_endpoint_for_no_existing_match(self, mock_get_match_by_id):
        # Arrange
        match_fixture = fixtures.match_fixture
        mock_get_match_by_id.side_effect = MatchNotFoundException

        # Act
        response = self.client.get(f"{MATCH_ENDPOINT_BASE_URL}/{match_fixture.id}")

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        mock_get_match_by_id.assert_called_once_with(match_fixture.id)