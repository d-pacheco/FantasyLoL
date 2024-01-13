import random

from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import Game
from fantasylol.schemas.game_state import GameState


class GameTestUtil:
    @staticmethod
    def create_completed_game(match_id: int = None):
        return create_game_in_db(GameState.COMPLETED, match_id)

    @staticmethod
    def create_inprogress_game(match_id: int = None):
        return create_game_in_db(GameState.INPROGRESS, match_id)

    @staticmethod
    def create_unstarted_game(match_id: int = None):
        return create_game_in_db(GameState.UNSTARTED, match_id)


def create_game_in_db(game_state: str, match_id: int):
    if match_id is None:
        match_id = random.randint(10000, 99999)
    mock_game_attrs = {
        "id": random.randint(10000, 99999),
        "state": game_state,
        "number": 2,
        "match_id": match_id,
    }
    game = Game(**mock_game_attrs)
    with DatabaseConnection() as db:
        db.add(game)
        db.commit()
        db.refresh(game)
    return game
