from fastapi import APIRouter
from fastapi import Query
from typing import List

from fantasylol.service.riot_league_service import RiotLeagueService
from fantasylol.schemas.riot_data_schemas import LeagueSchema
from fantasylol.schemas.search_parameters import LeagueSearchParameters


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
league_service = RiotLeagueService()


@router.get(
    path="/league",
    description="Get a list of leagues based on a set of search criteria",
    tags=["Leagues"],
    response_model=List[LeagueSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [LeagueSchema.ExampleResponse.example]
                }
            }
        }
    }
)
def get_riot_leagues(
        name: str = Query(None, description="Filter by league name"),
        region: str = Query(None, description="Filter by league region")):
    search_parameters = LeagueSearchParameters(
        name=name,
        region=region
    )
    leagues = league_service.get_leagues(search_parameters)
    leagues_response = [LeagueSchema(**league.to_dict()) for league in leagues]

    return leagues_response


@router.get(
    path="/league/{league_id}",
    description="Get league by its ID",
    tags=["Leagues"],
    response_model=LeagueSchema,
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": LeagueSchema.ExampleResponse.example
                }
            }
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
def get_riot_league_by_id(league_id: int):
    league = league_service.get_league_by_id(league_id)
    league_response = LeagueSchema(**league.to_dict())

    return league_response


@router.get(
    path="/fetch-leagues",
    description="fetch leagues from riots servers",
    tags=["Leagues"],
    response_model=List[LeagueSchema],
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": [LeagueSchema.ExampleResponse.example]
                }
            }
        }
    }
)
def fetch_leagues_from_riot():
    leagues = league_service.fetch_and_store_leagues()
    leagues_response = [LeagueSchema(**league.to_dict()) for league in leagues]

    return leagues_response
