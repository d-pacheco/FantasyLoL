import random

from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import Game
from fantasylol.schemas.game_state import GameState


class GameTestUtil:
    @staticmethod
    def create_completed_game(tournament_id: int):
        return create_game_in_db(GameState.COMPLETED, tournament_id)

    @staticmethod
    def create_inprogress_game(tournament_id: int):
        return create_game_in_db(GameState.INPROGRESS, tournament_id)

    @staticmethod
    def create_unstarted_game(tournament_id: int):
        return create_game_in_db(GameState.UNSTARTED, tournament_id)


def create_game_in_db(game_state: str, tournament_id: int):
    mock_game_attrs = {
        "id": random.randint(10000, 99999),
        "state": game_state,
        "number": 2,
        "match_id": random.randint(10000, 99999),
    }
    game = Game(**mock_game_attrs)
    with DatabaseConnection() as db:
        db.add(game)
        db.commit()
        db.refresh(game)
    return game
