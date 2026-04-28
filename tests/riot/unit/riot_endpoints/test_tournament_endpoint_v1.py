from http import HTTPStatus

import pytest

from tests.test_util import riot_fixtures as fixtures

from src.common.schemas.riot_data_schemas import TournamentStatus
from src.riot.exceptions import TournamentNotFoundException
from src.riot.endpoints import TournamentEndpoint

TOURNAMENT_BASE_URL = "/api/v1/tournament"


class TestTournamentEndpointV1:
    @pytest.mark.parametrize(
        "tournament_fixture,status",
        [
            (fixtures.active_tournament_fixture, TournamentStatus.ACTIVE),
            (fixtures.tournament_fixture, TournamentStatus.COMPLETED),
            (fixtures.future_tournament_fixture, TournamentStatus.UPCOMING),
        ],
        ids=["active", "completed", "upcoming"],
    )
    def test_get_tournaments_by_status(self, create_endpoint_client, tournament_fixture, status):
        client, mock = create_endpoint_client(TournamentEndpoint)
        mock.get_tournaments.return_value = [tournament_fixture]

        response = client.get(f"{TOURNAMENT_BASE_URL}?status={status.value}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"] == [tournament_fixture.model_dump()]

    def test_get_tournaments_invalid_status(self, create_endpoint_client):
        client, _ = create_endpoint_client(TournamentEndpoint)

        response = client.get(f"{TOURNAMENT_BASE_URL}?status=invalid")

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_tournament_by_id_success(self, create_endpoint_client):
        client, mock = create_endpoint_client(TournamentEndpoint)
        tournament = fixtures.tournament_fixture
        mock.get_tournament_by_id.return_value = tournament

        response = client.get(f"{TOURNAMENT_BASE_URL}/{tournament.id}")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == tournament.model_dump()

    def test_get_tournament_by_id_not_found(self, create_endpoint_client):
        client, mock = create_endpoint_client(TournamentEndpoint)
        tournament = fixtures.tournament_fixture
        mock.get_tournament_by_id.side_effect = TournamentNotFoundException()

        response = client.get(f"{TOURNAMENT_BASE_URL}/{tournament.id}")

        assert response.status_code == HTTPStatus.NOT_FOUND
