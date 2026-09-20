from http import HTTPStatus

import pytest

from tests.test_util import riot_fixtures as fixtures

from src.common.exceptions import ProfessionalPlayerNotFoundException
from src.riot.endpoints import ProfessionalPlayerEndpoint

PLAYER_BASE_URL = "/api/v1/professional-player"


class TestProfessionalPlayerEndpointV1:
    @pytest.mark.parametrize(
        "param,value_fn",
        [
            ("summoner_name", lambda p: p.summoner_name),
            ("role", lambda p: p.role.value),
            ("team_name", lambda p: p.team_name),
        ],
        ids=["summoner_name", "role", "team_name"],
    )
    def test_get_players_by_filter(self, create_endpoint_client, param, value_fn):
        client, mock = create_endpoint_client(ProfessionalPlayerEndpoint)
        player = fixtures.player_1_fixture
        mock.get_players.return_value = [player]

        response = client.get(f"{PLAYER_BASE_URL}?{param}={value_fn(player)}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [player.model_dump()]

    def test_get_players_search_all(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalPlayerEndpoint)
        player = fixtures.player_1_fixture
        mock.get_players.return_value = [player]

        response = client.get(PLAYER_BASE_URL)

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [player.model_dump()]

    def test_get_player_by_id_success(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalPlayerEndpoint)
        player = fixtures.player_1_fixture
        mock.get_player_by_id.return_value = player

        response = client.get(f"{PLAYER_BASE_URL}/{player.id}")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == player.model_dump()

    def test_get_player_by_id_not_found(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalPlayerEndpoint)
        player = fixtures.player_1_fixture
        mock.get_player_by_id.side_effect = ProfessionalPlayerNotFoundException()

        response = client.get(f"{PLAYER_BASE_URL}/{player.id}")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_player_match_history_success(self, create_endpoint_client):
        from src.common.schemas.riot_data_schemas import PlayerMatchHistoryEntry

        client, mock = create_endpoint_client(ProfessionalPlayerEndpoint)
        player = fixtures.player_1_fixture
        entry = PlayerMatchHistoryEntry(
            game_id="g1",
            player_id=player.id,
            kills=4,
            deaths=2,
            assists=6,
            opponent_code="T2",
            win=True,
            multi_kills=["double"],
        )
        mock.get_player_match_history.return_value = [entry]

        response = client.get(f"{PLAYER_BASE_URL}/{player.id}/match-history")

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert body["items"] == [entry.model_dump()]
        mock.get_player_match_history.assert_called_once_with(player.id)

    def test_get_player_match_history_not_found(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalPlayerEndpoint)
        player = fixtures.player_1_fixture
        mock.get_player_match_history.side_effect = ProfessionalPlayerNotFoundException()

        response = client.get(f"{PLAYER_BASE_URL}/{player.id}/match-history")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_player_summary_success(self, create_endpoint_client):
        from src.common.schemas.riot_data_schemas import PlayerCareerSummary

        client, mock = create_endpoint_client(ProfessionalPlayerEndpoint)
        player = fixtures.player_1_fixture
        summary = PlayerCareerSummary(
            player_id=player.id, games_played=3, kda_ratio=4.5, win_rate=66.67
        )
        mock.get_player_career_summary.return_value = summary

        response = client.get(f"{PLAYER_BASE_URL}/{player.id}/summary")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == summary.model_dump()
        mock.get_player_career_summary.assert_called_once_with(player.id)

    def test_get_player_summary_not_found(self, create_endpoint_client):
        client, mock = create_endpoint_client(ProfessionalPlayerEndpoint)
        player = fixtures.player_1_fixture
        mock.get_player_career_summary.side_effect = ProfessionalPlayerNotFoundException()

        response = client.get(f"{PLAYER_BASE_URL}/{player.id}/summary")

        assert response.status_code == HTTPStatus.NOT_FOUND
