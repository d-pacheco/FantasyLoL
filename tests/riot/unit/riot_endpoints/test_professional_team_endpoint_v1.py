from http import HTTPStatus

import pytest

from tests.test_util import riot_fixtures as fixtures

from src.riot.exceptions import ProfessionalTeamNotFoundException
from src.riot.endpoints import ProfessionalTeamEndpoint

TEAM_BASE_URL = "/api/v1/professional-team"


class TestProfessionalTeamEndpointV1:
    @pytest.mark.parametrize(
        "param,value_fn",
        [
            ("slug", lambda t: t.slug),
            ("name", lambda t: t.name),
            ("code", lambda t: t.code),
            ("status", lambda t: t.status),
            ("league", lambda t: t.home_league_name),
        ],
        ids=["slug", "name", "code", "status", "league"],
    )
    def test_get_teams_by_filter(self, create_endpoint_client, param, value_fn):
        client, mock = create_endpoint_client(ProfessionalTeamEndpoint)
        team = fixtures.team_1_fixture
        mock.get_teams.return_value = [team]

        response = client.get(f"{TEAM_BASE_URL}?{param}={value_fn(team)}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [team.model_dump()]

    def test_get_teams_search_all(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalTeamEndpoint)
        team = fixtures.team_1_fixture
        mock.get_teams.return_value = [team]

        response = client.get(TEAM_BASE_URL)

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [team.model_dump()]

    def test_get_team_by_id_success(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalTeamEndpoint)
        team = fixtures.team_1_fixture
        mock.get_team_by_id.return_value = team

        response = client.get(f"{TEAM_BASE_URL}/{team.id}")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == team.model_dump()

    def test_get_team_by_id_not_found(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalTeamEndpoint)
        team = fixtures.team_1_fixture
        mock.get_team_by_id.side_effect = ProfessionalTeamNotFoundException()

        response = client.get(f"{TEAM_BASE_URL}/{team.id}")

        assert response.status_code == HTTPStatus.NOT_FOUND
