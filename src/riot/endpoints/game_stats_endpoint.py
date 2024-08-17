import logging
from fastapi import APIRouter, Query, Depends
from fastapi_pagination import paginate, Page

from src.common.schemas.riot_data_schemas import PlayerGameData, RiotGameID, ProPlayerID
from src.common.schemas.search_parameters import PlayerGameStatsSearchParameters
from src.db.database_service import db_service

from src.riot.service import RiotGameStatsService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
game_stat_service = RiotGameStatsService(db_service)
logger = logging.getLogger('fantasy-lol')


def get_game_stat_service() -> RiotGameStatsService:
    return game_stat_service


@router.get(
    path="/stats/player",
    description="Search game stats for players",
    tags=["Game Stats"],
    response_model=Page[PlayerGameData],
    responses={
        200: {
            "model": Page[PlayerGameData]
        }
    }
)
def get_game_stats_for_game(
        game_id: RiotGameID = Query(None, description="Game id"),
        player_id: ProPlayerID = Query(None, description="The id of the player to search for"),
        service: RiotGameStatsService = Depends(get_game_stat_service)
) -> Page[PlayerGameData]:
    search_parameters = PlayerGameStatsSearchParameters(
        game_id=game_id,
        player_id=player_id
    )
    player_game_stats = service.get_player_stats(search_parameters)
    return paginate(player_game_stats)
