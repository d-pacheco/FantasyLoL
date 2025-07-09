import logging

from src.common.schemas.search_parameters import GameSearchParameters
from src.common.schemas.riot_data_schemas import Game, RiotGameID
from src.db.database_service import DatabaseService
from src.db.models import GameModel
from src.riot.exceptions import GameNotFoundException

logger = logging.getLogger('riot')


class RiotGameService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_games(self, search_parameters: GameSearchParameters) -> list[Game]:
        filters = []
        if search_parameters.state is not None:
            filters.append(GameModel.state == search_parameters.state)
        if search_parameters.match_id is not None:
            filters.append(GameModel.match_id == search_parameters.match_id)
        games = self.db.get_games(filters)
        return games

    def get_game_by_id(self, game_id: RiotGameID) -> Game:
        game = self.db.get_game_by_id(game_id)
        if game is None:
            raise GameNotFoundException()
        return game
