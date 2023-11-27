from fastapi import APIRouter
from fastapi import Query

from fantasylol.service.RiotLeagueService import RiotLeagueService
from fantasylol.schemas.riot_data_schemas import LeagueSchema

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
league_service = RiotLeagueService()

@router.get(
    path="/league",
    description="Get a list of leagues based on a set of search criteria",
    tags=["leagues"],
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
    query_params = {
        "name": name,
        "region": region
    }
    return league_service.get_leagues(query_params)

@router.get(
    path="/league/{league_id}",
    description="Get league by ID",
    tags=["leagues"],
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
            "description": "Not Found"
        }
    }
)
def get_riot_league_by_id(league_id: int):
    return league_service.get_league_by_id(league_id)

@router.get(
    path="/fetch-leagues",
    description="fetch leagues from riots servers",
    tags=["leagues"],
    response_model=LeagueSchema,
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
    return league_service.fetch_and_store_leagues()
