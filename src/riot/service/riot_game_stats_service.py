import logging

from src.common.schemas.search_parameters import PlayerGameStatsSearchParameters
from src.common.schemas.riot_data_schemas import PlayerGameData

from src.db.database_service import DatabaseService
from src.db.views import PlayerGameView

logger = logging.getLogger("riot")


class RiotGameStatsService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_player_stats(
        self, search_parameters: PlayerGameStatsSearchParameters
    ) -> list[PlayerGameData]:
        filters = []
        if search_parameters.game_id is not None:
            filters.append(PlayerGameView.game_id == search_parameters.game_id)
        if search_parameters.player_id is not None:
            filters.append(PlayerGameView.player_id == search_parameters.player_id)
        player_game_stats = self.db.get_player_game_stats(filters)
        sorted_player_game_stats = sorted(
            player_game_stats, key=lambda x: (x.game_id, x.participant_id)
        )
        return sorted_player_game_stats
