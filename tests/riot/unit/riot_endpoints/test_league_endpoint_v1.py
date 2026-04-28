from http import HTTPStatus

from tests.test_util import riot_fixtures as fixtures

from src.common.exceptions import LeagueNotFoundException
from src.common.schemas.search_parameters import LeagueSearchParameters
from src.riot.endpoints import LeagueEndpoint

LEAGUE_BASE_URL = "/api/v1/league"


class TestLeagueEndpointV1:
    def test_get_leagues_search_all(self, create_endpoint_client):
        client, mock = create_endpoint_client(LeagueEndpoint)
        league = fixtures.league_1_fixture
        mock.get_leagues.return_value = [league]

        response = client.get(LEAGUE_BASE_URL)

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [league.model_dump()]
        mock.get_leagues.assert_called_once_with(LeagueSearchParameters())

    def test_get_leagues_name_filter(self, create_endpoint_client):
        client, mock = create_endpoint_client(LeagueEndpoint)
        league = fixtures.league_1_fixture
        mock.get_leagues.return_value = [league]

        response = client.get(f"{LEAGUE_BASE_URL}?name={league.name}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [league.model_dump()]
        mock.get_leagues.assert_called_once_with(LeagueSearchParameters(name=league.name))

    def test_get_leagues_region_filter(self, create_endpoint_client):
        client, mock = create_endpoint_client(LeagueEndpoint)
        league = fixtures.league_1_fixture
        mock.get_leagues.return_value = [league]

        response = client.get(f"{LEAGUE_BASE_URL}?region={league.region}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [league.model_dump()]
        mock.get_leagues.assert_called_once_with(LeagueSearchParameters(region=league.region))

    def test_get_leagues_fantasy_available_filter(self, create_endpoint_client):
        client, mock = create_endpoint_client(LeagueEndpoint)
        league = fixtures.league_1_fixture
        mock.get_leagues.return_value = [league]

        response = client.get(f"{LEAGUE_BASE_URL}?fantasy_available={league.fantasy_available}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [league.model_dump()]
        mock.get_leagues.assert_called_once_with(
            LeagueSearchParameters(fantasy_available=league.fantasy_available)
        )

    def test_get_league_by_id_success(self, create_endpoint_client):
        client, mock = create_endpoint_client(LeagueEndpoint)
        league = fixtures.league_1_fixture
        mock.get_league_by_id.return_value = league

        response = client.get(f"{LEAGUE_BASE_URL}/{league.id}")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == league.model_dump()

    def test_get_league_by_id_not_found(self, create_endpoint_client):
        client, mock = create_endpoint_client(LeagueEndpoint)
        league = fixtures.league_1_fixture
        mock.get_league_by_id.side_effect = LeagueNotFoundException(league.id)

        response = client.get(f"{LEAGUE_BASE_URL}/{league.id}")

        assert response.status_code == HTTPStatus.NOT_FOUND
