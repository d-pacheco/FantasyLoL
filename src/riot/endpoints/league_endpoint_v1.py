from fastapi import APIRouter, Query, Depends
from fastapi_pagination import paginate, Page

from src.common.schemas.riot_data_schemas import League, RiotLeagueID
from src.common.schemas.search_parameters import LeagueSearchParameters
from src.db.database_service import db_service
from src.riot.service import RiotLeagueService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
league_service = RiotLeagueService(db_service)


def get_league_service() -> RiotLeagueService:
    return league_service


@router.get(
    path="/league",
    description="Get a list of leagues based on a set of search criteria",
    tags=["Leagues"],
    response_model=Page[League],
    responses={
        200: {
            "model": Page[League]
        }
    }
)
def get_riot_leagues(
        name: str = Query(None, description="Filter by league name"),
        region: str = Query(None, description="Filter by league region"),
        fantasy_available: bool = Query(None, description="Filter by availability in Fantasy LoL"),
        service: RiotLeagueService = Depends(get_league_service)
) -> Page[League]:
    search_parameters = LeagueSearchParameters(
        name=name,
        region=region,
        fantasy_available=fantasy_available
    )
    leagues = service.get_leagues(search_parameters)
    return paginate(leagues)


@router.get(
    path="/league/{league_id}",
    description="Get league by its ID",
    tags=["Leagues"],
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
        league_id: RiotLeagueID,
        service: RiotLeagueService = Depends(get_league_service)
) -> League:
    return service.get_league_by_id(league_id)


@router.put(
    path="/league/{league_id}/{new_status}",
    description="Update league to be available for fantasy leagues",
    tags=["Leagues"],
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
        league_id: RiotLeagueID,
        new_status: bool,
        service: RiotLeagueService = Depends(get_league_service)
) -> League:
    return service.update_fantasy_available(league_id, new_status)
