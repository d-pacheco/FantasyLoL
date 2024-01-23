import logging
from fastapi import APIRouter, Query
from fastapi_pagination import paginate, Page

from fantasylol.service.riot_match_service import RiotMatchService
from fantasylol.schemas.riot_data_schemas import Match
from fantasylol.schemas.search_parameters import MatchSearchParameters

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
match_service = RiotMatchService()
logger = logging.getLogger('fantasy-lol')


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
        tournament_id: str = Query(None, description="Filter by tournament id")):
    search_parameters = MatchSearchParameters(
        league_slug=league_slug,
        tournament_id=tournament_id
    )
    matches = match_service.get_matches(search_parameters)
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
def get_riot_match_by_id(match_id: str):
    return match_service.get_match_by_id(match_id)
