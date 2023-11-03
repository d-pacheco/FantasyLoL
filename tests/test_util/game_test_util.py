import datetime
import random

from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import Game
from fantasylol.util.game_state import GameState

class GameTestUtil:
    def create_completed_game(tournament_id: int):
        return create_game_in_db(GameState.COMPLETED, tournament_id)
    
    def create_inprogress_game(tournament_id: int):
        return create_game_in_db(GameState.INPROGRESS, tournament_id)
    
    def create_unstarted_game(tournament_id: int):
        return create_game_in_db(GameState.UNSTARTED, tournament_id)


def create_game_in_db(game_state: str, tournament_id: int):
    today = datetime.date.today()
    if game_state == GameState.COMPLETED:
        start_time = today + datetime.timedelta(days=-3)
    elif game_state == GameState.INPROGRESS:
        start_time = today + datetime.timedelta(minutes=-10)
    else:
        start_time = today + datetime.timedelta(days=3)

    mock_game_attrs = {
        "id": random.randint(10000, 99999),
        "start_time": start_time,
        "block_name": "Playoffs - Round 1",
        "strategy_type": "bestOf",
        "strategy_count": 5,
        "state": game_state,
        "number": 2,
        "tournament_id": tournament_id,
        "team_1_id": random.randint(10000, 99999),
        "team_2_id": random.randint(10000, 99999),
    }
    game = Game(**mock_game_attrs)
    with DatabaseConnection() as db:
        db.add(game)
        db.commit()
        db.refresh(game)
    return game
