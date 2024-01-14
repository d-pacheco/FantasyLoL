import logging
from fastapi import APIRouter
from fastapi import Query
from fastapi import status
from typing import List

from fantasylol.service.riot_match_service import RiotMatchService
from fantasylol.schemas.riot_data_schemas import MatchSchema
from fantasylol.schemas.search_parameters import MatchSearchParameters
from fantasylol.exceptions.fantasy_lol_exception import FantasyLolException

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
match_service = RiotMatchService()
logger = logging.getLogger('fantasy-lol')


@router.get(
    path="/matches",
    description="Get a list of matches based on a set of search criteria",
    tags=["Matches"],
    response_model=List[MatchSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [MatchSchema.ExampleResponse.example]
                }
            }
        }
    }
)
def get_riot_matches(
        league_slug: str = Query(None, description="Filter by league name"),
        tournament_id: int = Query(None, description="Filter by tournament id")):
    search_parameters = MatchSearchParameters(
        league_slug=league_slug,
        tournament_id=tournament_id
    )
    matches = match_service.get_matches(search_parameters)
    matches_response = [MatchSchema(**match.to_dict()) for match in matches]
    return matches_response


@router.get(
    path="/matches/{match_id}",
    description="Get a match by its ID",
    tags=["Matches"],
    response_model=MatchSchema,
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": MatchSchema.ExampleResponse.example
                }
            }
        }
    }
)
def get_riot_match_by_id(match_id: int):
    match = match_service.get_match_by_id(match_id)
    match_response = MatchSchema(**match.to_dict())
    return match_response


@router.get(
    path="/fetch-matches/{tournament_id}",
    description="Fetch matches for a tournament from riots servers",
    tags=["Matches"],
    response_model=List[MatchSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [MatchSchema.ExampleResponse.example]
                }
            }
        }
    }
)
def fetch_matches_with_tournament_id_from_riot(tournament_id: int):
    matches = match_service.fetch_and_store_matchs_from_tournament(tournament_id)
    matches_response = [MatchSchema(**match.to_dict()) for match in matches]
    return matches_response


@router.get(
    path="/fetch-all-matches",
    description="Fetch matches for all tournament from riots servers",
    tags=["Matches"],
    response_model=List[MatchSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [MatchSchema.ExampleResponse.example]
                }
            }
        }
    }
)
def fetch_all_matches_for_all_tournaments():
    matches = match_service.get_all_matches()
    matches_response = [MatchSchema(**match.to_dict()) for match in matches]
    return matches_response


@router.get(
    path="/fetch-new-schedule",
    description="Fetch schedule from riots servers",
    tags=["Matches"],
    status_code=status.HTTP_200_OK
)
def fetch_new_schedule():
    schedule_updated = match_service.fetch_new_schedule()
    if schedule_updated:
        logger.info("Schedule has been updated")
        return "Schedule has been updated"
    else:
        logger.info("Schedule up to date")
        return "Schedule up to date"


@router.get(
    path="/fetch-entire-schedule",
    description="Fetch entire schedule from riots servers. "
                "This should only ever be used once for a new deployment. "
                "This task usually takes 30 to 45 minutes to complete",
    tags=["Matches"]
)
def fetch_entire_schedule():
    max_retries = 3
    retry_count = 0
    completed_fetch = False
    while retry_count <= max_retries and not completed_fetch:
        try:
            match_service.fetch_entire_schedule()
            completed_fetch = True
        except FantasyLolException:
            retry_count += 1
            logger.warning(f"An error occurred. Retry attempt: {retry_count}")
    if completed_fetch:
        return "Entire schedule fetched and saved"
    else:
        logger.error("Failed to fetch the entire schedule")
        return "Failed to fetch schedule from riot"
