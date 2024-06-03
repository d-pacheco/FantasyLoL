import logging
from fastapi import APIRouter, Query
from fastapi_pagination import paginate, Page

from ...common.schemas.riot_data_schemas import PlayerGameData, RiotGameID, ProPlayerID
from ...common.schemas.search_parameters import PlayerGameStatsSearchParameters

from ..service.riot_game_stats_service import RiotGameStatsService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
game_stat_service = RiotGameStatsService()
logger = logging.getLogger('fantasy-lol')


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
        player_id: ProPlayerID = Query(None, description="The id of the player to search for")
) -> Page[PlayerGameData]:
    search_parameters = PlayerGameStatsSearchParameters(
        game_id=game_id,
        player_id=player_id
    )
    player_game_stats = game_stat_service.get_player_stats(search_parameters)
    return paginate(player_game_stats)
