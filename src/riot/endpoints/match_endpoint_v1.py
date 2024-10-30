from classy_fastapi import Routable, get
from fastapi import Query, Depends
from fastapi_pagination import paginate, Page

from src.auth import Permissions, JWTBearer
from src.common.schemas.riot_data_schemas import Match, RiotMatchID, RiotTournamentID
from src.common.schemas.search_parameters import MatchSearchParameters
from src.riot.service import RiotMatchService


class MatchEndpoint(Routable):
    def __init__(self, match_service: RiotMatchService):
        super().__init__()
        self.__match_service = match_service

    @get(
        path="/matches",
        description="Get a list of matches based on a set of search criteria",
        tags=["Matches"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_READ]))],
        response_model=Page[Match],
        responses={
            200: {
                "model": Page[Match]
            }
        }
    )
    def get_riot_matches(
            self,
            league_slug: str = Query(None, description="Filter by league name"),
            tournament_id: RiotTournamentID = Query(None, description="Filter by tournament id")
    ) -> Page[Match]:
        search_parameters = MatchSearchParameters(
            league_slug=league_slug,
            tournament_id=tournament_id
        )
        matches = self.__match_service.get_matches(search_parameters)
        return paginate(matches)

    @get(
        path="/matches/{match_id}",
        description="Get a match by its ID",
        tags=["Matches"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_READ]))],
        response_model=Match,
        responses={
            200: {
                "model": Match
            }
        }
    )
    def get_riot_match_by_id(
            self,
            match_id: RiotMatchID
    ) -> Match:
        return self.__match_service.get_match_by_id(match_id)
