from http import HTTPStatus

from tests.test_util import riot_fixtures as fixtures

from src.riot.exceptions import MatchNotFoundException
from src.riot.endpoints import MatchEndpoint

MATCH_BASE_URL = "/api/v1/matches"


class TestMatchEndpointV1:
    def test_get_matches_search_all(self, create_endpoint_client):
        client, mock = create_endpoint_client(MatchEndpoint)
        match = fixtures.match_fixture
        mock.get_matches.return_value = [match]

        response = client.get(MATCH_BASE_URL)

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [match.model_dump()]

    def test_get_matches_filter_by_league_slug(self, create_endpoint_client):
        client, mock = create_endpoint_client(MatchEndpoint)
        match = fixtures.match_fixture
        mock.get_matches.return_value = [match]

        response = client.get(f"{MATCH_BASE_URL}?league_slug={match.league_slug}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [match.model_dump()]

    def test_get_matches_filter_by_tournament_id(self, create_endpoint_client):
        client, mock = create_endpoint_client(MatchEndpoint)
        match = fixtures.match_fixture
        mock.get_matches.return_value = [match]

        response = client.get(f"{MATCH_BASE_URL}?tournament_id={match.tournament_id}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [match.model_dump()]

    def test_get_match_by_id_success(self, create_endpoint_client):
        client, mock = create_endpoint_client(MatchEndpoint)
        match = fixtures.match_fixture
        mock.get_match_by_id.return_value = match

        response = client.get(f"{MATCH_BASE_URL}/{match.id}")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == match.model_dump()

    def test_get_match_by_id_not_found(self, create_endpoint_client):
        client, mock = create_endpoint_client(MatchEndpoint)
        match = fixtures.match_fixture
        mock.get_match_by_id.side_effect = MatchNotFoundException()

        response = client.get(f"{MATCH_BASE_URL}/{match.id}")

        assert response.status_code == HTTPStatus.NOT_FOUND
