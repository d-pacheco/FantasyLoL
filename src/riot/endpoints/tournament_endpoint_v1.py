from classy_fastapi import Routable, get
from fastapi import Depends, Query
from fastapi_pagination import paginate, Page

from src.auth import JWTBearer, Permissions
from src.common.schemas.riot_data_schemas import Tournament, TournamentStatus, RiotTournamentID
from src.common.schemas.search_parameters import TournamentSearchParameters
from src.riot.service import RiotTournamentService


def validate_status_parameter(status: TournamentStatus = Query(
        None, description="Status of tournament")):
    return status


class TournamentEndpoint(Routable):
    def __init__(self, tournament_service: RiotTournamentService):
        super().__init__()
        self.__tournament_service = tournament_service

    @get(
        path="/tournament",
        description="Get a list of tournaments based on a set of search criteria",
        tags=["Tournaments"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_READ]))],
        response_model=Page[Tournament],
        responses={
            200: {
                "model": Page[Tournament]
            }
        }
    )
    def get_riot_tournaments(
            self,
            status: TournamentStatus = Depends(validate_status_parameter)
    ) -> Page[Tournament]:
        search_parameters = TournamentSearchParameters(status=status)
        tournaments = self.__tournament_service.get_tournaments(search_parameters)
        return paginate(tournaments)

    @get(
        path="/tournament/{tournament_id}",
        description="Get a tournament by its ID",
        tags=["Tournaments"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_READ]))],
        response_model=Tournament,
        responses={
            200: {
                "model": Tournament
            },
            404: {
                "description": "Not Found",
                "content": {
                    "application/json": {
                        "example": {"detail": "Tournament not found"}
                    }
                }
            }
        }
    )
    def get_riot_tournaments_by_id(
            self,
            tournament_id: RiotTournamentID
    ) -> Tournament:
        return self.__tournament_service.get_tournament_by_id(tournament_id)
