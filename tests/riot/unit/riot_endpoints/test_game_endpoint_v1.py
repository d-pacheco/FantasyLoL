from http import HTTPStatus

import pytest

from tests.test_util import riot_fixtures as fixtures

from src.common.schemas.riot_data_schemas import GameState
from src.riot.exceptions import GameNotFoundException
from src.riot.endpoints import GameEndpoint

GAME_BASE_URL = "/api/v1/game"


class TestGameEndpointV1:
    @pytest.mark.parametrize(
        "game_fixture,state",
        [
            (fixtures.game_1_fixture_completed, GameState.COMPLETED),
            (fixtures.game_2_fixture_inprogress, GameState.INPROGRESS),
            (fixtures.game_3_fixture_unstarted, GameState.UNSTARTED),
            (fixtures.game_4_fixture_unneeded, GameState.UNNEEDED),
        ],
        ids=["completed", "inprogress", "unstarted", "unneeded"],
    )
    def test_get_game_by_state(self, create_endpoint_client, game_fixture, state):
        client, mock = create_endpoint_client(GameEndpoint)
        mock.get_games.return_value = [game_fixture]

        response = client.get(f"{GAME_BASE_URL}?state={state.value}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [game_fixture.model_dump()]

    def test_get_game_invalid_status(self, create_endpoint_client):
        client, _ = create_endpoint_client(GameEndpoint)

        response = client.get(f"{GAME_BASE_URL}?state=invalid")

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_game_match_id_filter(self, create_endpoint_client):
        client, mock = create_endpoint_client(GameEndpoint)
        game = fixtures.game_1_fixture_completed
        mock.get_games.return_value = [game]

        response = client.get(f"{GAME_BASE_URL}?match_id={game.match_id}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [game.model_dump()]

    def test_get_game_by_id_success(self, create_endpoint_client):
        client, mock = create_endpoint_client(GameEndpoint)
        game = fixtures.game_1_fixture_completed
        mock.get_game_by_id.return_value = game

        response = client.get(f"{GAME_BASE_URL}/{game.id}")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == game.model_dump()

    def test_get_game_by_id_not_found(self, create_endpoint_client):
        client, mock = create_endpoint_client(GameEndpoint)
        mock.get_game_by_id.side_effect = GameNotFoundException()

        response = client.get(f"{GAME_BASE_URL}/777")

        assert response.status_code == HTTPStatus.NOT_FOUND
