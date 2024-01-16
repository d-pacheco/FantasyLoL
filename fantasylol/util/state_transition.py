from sqlalchemy import event
from fantasylol.db import models
from fantasylol.schemas.game_state import GameState
from fantasylol.service.riot_game_stats_service import RiotGameStatsService
import logging

logger = logging.getLogger('fantasy-lol')


def on_game_state_transition(target, value, old_value, initiator):
    if value == GameState.COMPLETED.value and old_value.value == GameState.INPROGRESS.value:
        logger.info(f"Game {target.id}: State transition from INPROGRESS to COMPLETED")
        game_stats_service = RiotGameStatsService()
        game_stats_service.fetch_and_store_player_metadata_for_game(target.id)
        game_stats_service.fetch_and_store_player_stats_for_game(target.id)

    return value


class StateTransitionHandler:
    @staticmethod
    def configure_listeners():
        event.listen(models.Game.state, 'set', on_game_state_transition, retval=True)
