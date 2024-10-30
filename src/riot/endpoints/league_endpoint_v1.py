from classy_fastapi import Routable, get, put
from fastapi import Query, Depends
from fastapi_pagination import paginate, Page

from src.auth import JWTBearer, Permissions
from src.common.schemas.riot_data_schemas import League, RiotLeagueID
from src.common.schemas.search_parameters import LeagueSearchParameters
from src.riot.service import RiotLeagueService


class LeagueEndpoint(Routable):
    def __init__(self, league_service: RiotLeagueService):
        super().__init__()
        self.__league_service = league_service

    @get(
        path="/league",
        description="Get a list of leagues based on a set of search criteria",
        tags=["Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_READ]))],
        response_model=Page[League],
        responses={
            200: {
                "model": Page[League]
            }
        }
    )
    def get_riot_leagues(
            self,
            name: str = Query(None, description="Filter by league name"),
            region: str = Query(None, description="Filter by league region"),
            fantasy_available: bool = Query(
                None, description="Filter by availability in Fantasy LoL")
    ) -> Page[League]:
        search_parameters = LeagueSearchParameters(
            name=name,
            region=region,
            fantasy_available=fantasy_available
        )
        leagues = self.__league_service.get_leagues(search_parameters)
        return paginate(leagues)

    @get(
        path="/league/{league_id}",
        description="Get league by its ID",
        tags=["Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_READ]))],
        response_model=League,
        responses={
            200: {
                "model": League
            },
            404: {
                "description": "Not Found",
                "content": {
                    "application/json": {
                        "example": {"detail": "League not found"}
                    }
                }
            }
        }
    )
    def get_riot_league_by_id(
            self,
            league_id: RiotLeagueID
    ) -> League:
        return self.__league_service.get_league_by_id(league_id)

    @put(
        path="/league/{league_id}/{new_status}",
        description="Update league to be available for fantasy leagues",
        tags=["Leagues"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_WRITE]))],
        response_model=League,
        responses={
            200: {
                "model": League
            },
            404: {
                "description": "Not Found",
                "content": {
                    "application/json": {
                        "example": {"detail": "League not found"}
                    }
                }
            }
        }
    )
    def update_riot_league_fantasy_available(
            self,
            league_id: RiotLeagueID,
            new_status: bool
    ) -> League:
        return self.__league_service.update_fantasy_available(league_id, new_status)
