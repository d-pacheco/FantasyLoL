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
            ("team_id", lambda p: p.team_id),
        ],
        ids=["summoner_name", "role", "team_id"],
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
