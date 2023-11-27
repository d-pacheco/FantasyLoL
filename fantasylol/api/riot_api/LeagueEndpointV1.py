from fastapi import APIRouter
from fastapi import Query

from fantasylol.service.RiotLeagueService import RiotLeagueService

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
league_service = RiotLeagueService()

@router.get("/league")
def get_riot_leagues(
        name: str = Query(None, description="Filter by league name"),
        region: str = Query(None, description="Filter by league region")):
    query_params = {
        "name": name,
        "region": region
    }
    return league_service.get_leagues(query_params)

@router.get("/league/{league_id}")
def get_riot_league_by_id(league_id: int):
    return league_service.get_league_by_id(league_id)

@router.get("/fetch-leagues")
def fetch_leagues_from_riot():
    return league_service.fetch_and_store_leagues()
