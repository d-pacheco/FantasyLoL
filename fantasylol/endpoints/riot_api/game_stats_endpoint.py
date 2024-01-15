import logging
from fastapi import APIRouter
from fastapi import Query

from fantasylol.service.riot_game_stats_service import RiotGameStatsService

VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
game_stat_service = RiotGameStatsService()
logger = logging.getLogger('fantasy-lol')


@router.get("/game-stat-player-stats")
def game_stat_job(game_id: str = Query(None, description="Game id")):
    game_stat_service.fetch_and_store_player_stats_for_game(game_id)


@router.get("/game-stat-player-metadata")
def game_stat_metadata(game_id: str = Query(None, description="Game id")):
    game_stat_service.fetch_and_store_player_metadata_for_game(game_id)
