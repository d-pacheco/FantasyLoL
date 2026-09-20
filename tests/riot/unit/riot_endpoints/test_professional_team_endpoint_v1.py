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

    def test_get_team_roster_success(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalTeamEndpoint)
        team = fixtures.team_1_fixture
        player = fixtures.player_1_fixture
        mock.get_team_roster.return_value = [player]

        response = client.get(f"{TEAM_BASE_URL}/{team.id}/roster")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == [player.model_dump()]
        mock.get_team_roster.assert_called_once_with(team.id)

    def test_get_team_roster_not_found(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalTeamEndpoint)
        team = fixtures.team_1_fixture
        mock.get_team_roster.side_effect = ProfessionalTeamNotFoundException()

        response = client.get(f"{TEAM_BASE_URL}/{team.id}/roster")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_team_match_history_success(self, create_endpoint_client):
        from src.common.schemas.riot_data_schemas import TeamMatchHistoryEntry

        client, mock = create_endpoint_client(ProfessionalTeamEndpoint)
        team = fixtures.team_1_fixture
        entry = TeamMatchHistoryEntry(
            match_id="m1", opponent_code="OPP", win=True, team_score=2, opponent_score=1
        )
        mock.get_team_match_history.return_value = [entry]

        response = client.get(f"{TEAM_BASE_URL}/{team.id}/match-history")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [entry.model_dump()]
        mock.get_team_match_history.assert_called_once_with(team.id)

    def test_get_team_summary_success(self, create_endpoint_client):
        from src.common.schemas.riot_data_schemas import TeamSummary

        client, mock = create_endpoint_client(ProfessionalTeamEndpoint)
        team = fixtures.team_1_fixture
        summary = TeamSummary(team_id=team.id, matches_played=5, wins=3, losses=2, win_rate=60.0)
        mock.get_team_summary.return_value = summary

        response = client.get(f"{TEAM_BASE_URL}/{team.id}/summary")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == summary.model_dump()
        mock.get_team_summary.assert_called_once_with(team.id)

    def test_get_team_summary_not_found(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalTeamEndpoint)
        team = fixtures.team_1_fixture
        mock.get_team_summary.side_effect = ProfessionalTeamNotFoundException()

        response = client.get(f"{TEAM_BASE_URL}/{team.id}/summary")

        assert response.status_code == HTTPStatus.NOT_FOUND
