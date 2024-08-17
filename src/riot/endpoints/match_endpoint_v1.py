import logging
from fastapi import APIRouter, Query, Depends
from fastapi_pagination import paginate, Page

from src.common.schemas.riot_data_schemas import Match, RiotMatchID, RiotTournamentID
from src.common.schemas.search_parameters import MatchSearchParameters
from src.db.database_service import db_service

from src.riot.service import RiotMatchService

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
match_service = RiotMatchService(db_service)
logger = logging.getLogger('fantasy-lol')


def get_match_service() -> RiotMatchService:
    return match_service


@router.get(
    path="/matches",
    description="Get a list of matches based on a set of search criteria",
    tags=["Matches"],
    response_model=Page[Match],
    responses={
        200: {
            "model": Page[Match]
        }
    }
)
def get_riot_matches(
        league_slug: str = Query(None, description="Filter by league name"),
        tournament_id: RiotTournamentID = Query(None, description="Filter by tournament id"),
        service: RiotMatchService = Depends(get_match_service)
) -> Page[Match]:
    search_parameters = MatchSearchParameters(
        league_slug=league_slug,
        tournament_id=tournament_id
    )
    matches = service.get_matches(search_parameters)
    return paginate(matches)


@router.get(
    path="/matches/{match_id}",
    description="Get a match by its ID",
    tags=["Matches"],
    response_model=Match,
    responses={
        200: {
            "model": Match
        }
    }
)
def get_riot_match_by_id(
        match_id: RiotMatchID,
        service: RiotMatchService = Depends(get_match_service)
) -> Match:
    return service.get_match_by_id(match_id)
