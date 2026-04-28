from http import HTTPStatus

import pytest

from tests.test_util import riot_fixtures as fixtures

from src.riot.endpoints import GameStatsEndpoint

GAME_STATS_BASE_URL = "/api/v1/stats"


class TestGameStatsEndpointV1:
    @pytest.mark.parametrize(
        "param,value_fn",
        [
            (None, None),
            ("game_id", lambda f: f.game_id),
            ("player_id", lambda f: f.player_id),
        ],
        ids=["no_filter", "game_id", "player_id"],
    )
    def test_get_player_stats_existing_data(self, create_endpoint_client, param, value_fn):
        client, mock = create_endpoint_client(GameStatsEndpoint)
        fixture = fixtures.player_1_game_data_fixture
        mock.get_player_stats.return_value = [fixture]

        url = f"{GAME_STATS_BASE_URL}/player"
        if param:
            url += f"?{param}={value_fn(fixture)}"

        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [fixture.model_dump()]

    @pytest.mark.parametrize(
        "param,value_fn",
        [
            (None, None),
            ("game_id", lambda f: f.game_id),
            ("player_id", lambda f: f.player_id),
        ],
        ids=["no_filter", "game_id", "player_id"],
    )
    def test_get_player_stats_no_data(self, create_endpoint_client, param, value_fn):
        client, mock = create_endpoint_client(GameStatsEndpoint)
        fixture = fixtures.player_1_game_data_fixture
        mock.get_player_stats.return_value = []

        url = f"{GAME_STATS_BASE_URL}/player"
        if param:
            url += f"?{param}={value_fn(fixture)}"

        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == []
