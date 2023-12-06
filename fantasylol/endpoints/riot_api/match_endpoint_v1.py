from fastapi import APIRouter
from fastapi import Query
from typing import List

from fantasylol.service.riot_match_service import RiotMatchService
from fantasylol.schemas.riot_data_schemas import MatchSchema

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
match_service = RiotMatchService()


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
        league_name: str = Query(None, description="Filter by league name"),
        tournament_id: int = Query(None, description="Filter by tournament id")):
    query_params = {
        "league_name": league_name,
        "tournament_id": tournament_id
    }
    matches = match_service.get_matches(query_params)
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
    path="fetch-all-matches",
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
