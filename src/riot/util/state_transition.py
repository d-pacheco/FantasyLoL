from sqlalchemy import event
import logging
import threading

from src.common.schemas.riot_data_schemas import GameState

from src.db import models
from src.db.database_service import db_service
from src.riot.service.riot_game_stats_service import RiotGameStatsService

logger = logging.getLogger('fantasy-lol')
game_stats_service = RiotGameStatsService(db_service)


def on_game_state_transition(mapper, connection, target):
    if target.state == GameState.COMPLETED:
        logger.info(f"Game {target.id}: State transition from INPROGRESS to COMPLETED")
        threading.Thread(target=fetch_player_data_async, args=(target.id,)).start()


def fetch_player_data_async(game_id):
    try:
        game_stats_service.fetch_and_store_player_metadata_for_game(game_id)
        game_stats_service.fetch_and_store_player_stats_for_game(game_id)
    except Exception as e:
        logger.error(f"Error processing player data for game {game_id}: {e}")


class StateTransitionHandler:
    @staticmethod
    def configure_listeners():
        event.listen(models.GameModel, 'after_update', on_game_state_transition, retval=True)
