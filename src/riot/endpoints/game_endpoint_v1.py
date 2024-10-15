from classy_fastapi import Routable, get
from fastapi import Depends, Query
from fastapi_pagination import paginate, Page

from src.common.schemas.riot_data_schemas import Game, GameState, RiotGameID, RiotMatchID
from src.common.schemas.search_parameters import GameSearchParameters
from src.riot.service import RiotGameService


def validate_status_parameter(state: GameState = Query(None, description="Filter by game state")):
    return state


class GameEndpoint(Routable):
    def __init__(self, game_service: RiotGameService):
        super().__init__()
        self.__game_service = game_service

    @get(
        path="/game",
        description="Get a list of games based on a set of search criteria",
        tags=["Games"],
        response_model=Page[Game],
        responses={
            200: {
                "model": Page[Game]
            }
        }
    )
    def get_riot_games(
            self,
            state: GameState = Depends(validate_status_parameter),
            match_id: RiotMatchID = Query(None, description="Filter by game match id")
    ) -> Page[Game]:
        search_parameters = GameSearchParameters(
            state=state,
            match_id=match_id
        )
        games = self.__game_service.get_games(search_parameters)
        return paginate(games)

    @get(
        path="/game/{game_id}",
        description="Get game by its ID",
        tags=["Games"],
        response_model=Game,
        responses={
            200: {
                "model": Game
            },
            404: {
                "description": "Not Found",
                "content": {
                    "application/json": {
                        "example": {"detail": "Game not found"}
                    }
                }
            }
        }
    )
    def get_riot_game_by_id(
            self,
            game_id: RiotGameID
    ) -> Game:
        return self.__game_service.get_game_by_id(game_id)
