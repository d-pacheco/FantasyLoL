from classy_fastapi import Routable, get
from fastapi import Query, Depends
from fastapi_pagination import paginate, Page

from src.auth import JWTBearer, Permissions
from src.common.schemas.riot_data_schemas import PlayerGameData, RiotGameID, ProPlayerID
from src.common.schemas.search_parameters import PlayerGameStatsSearchParameters
from src.riot.service import RiotGameStatsService


class GameStatsEndpoint(Routable):
    def __init__(self, game_stats_service: RiotGameStatsService):
        super().__init__()
        self.__game_stats_service = game_stats_service

    @get(
        path="/stats/player",
        description="Search game stats for players",
        tags=["Game Stats"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_READ]))],
        response_model=Page[PlayerGameData],
        responses={
            200: {
                "model": Page[PlayerGameData]
            }
        }
    )
    def get_game_stats_for_game(
            self,
            game_id: RiotGameID = Query(None, description="Game id"),
            player_id: ProPlayerID = Query(None, description="The id of the player to search for")
    ) -> Page[PlayerGameData]:
        search_parameters = PlayerGameStatsSearchParameters(
            game_id=game_id,
            player_id=player_id
        )
        player_game_stats = self.__game_stats_service.get_player_stats(search_parameters)
        return paginate(player_game_stats)
