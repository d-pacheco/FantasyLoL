from sqlalchemy import text
from typing import Optional, List

from src.common.schemas.riot_data_schemas import Game, RiotGameID, GameState
from src.db.models import GameModel


def put_game(session, game: Game) -> None:
    db_game = GameModel(**game.model_dump())
    session.merge(db_game)
    session.commit()


def bulk_save_games(session, games: List[Game]) -> None:
    db_games = [GameModel(**game.model_dump()) for game in games]
    session.bulk_save_objects(db_games)
    session.commit()


def update_has_game_data(session, game_id: RiotGameID, has_game_data: bool) -> None:
    db_game: GameModel = session.query(GameModel).filter(GameModel.id == game_id).first()
    if db_game is not None:
        db_game.has_game_data = has_game_data
        session.merge(db_game)
        session.commit()


def update_game_state(session, game_id: RiotGameID, state: GameState) -> None:
    db_game: Optional[GameModel] = session.query(GameModel).filter(GameModel.id == game_id).first()
    if db_game is not None:
        db_game.state = state
        session.merge(db_game)
        session.commit()


def update_game_last_stats_fetch(session, game_id: RiotGameID, last_fetch: bool) -> None:
    db_game: GameModel = session.query(GameModel).filter(GameModel.id == game_id).first()
    if db_game is not None:
        db_game.last_stats_fetch = last_fetch
        session.merge(db_game)
        session.commit()


def get_games_with_last_stats_fetch(session, last_stats_fetch: bool) -> List[Game]:
    game_models: List[GameModel] = session.query(GameModel)\
        .filter(GameModel.last_stats_fetch == last_stats_fetch).all()
    return [Game.model_validate(game_model) for game_model in game_models]


def get_games(session, filters: Optional[list] = None) -> List[Game]:
    if filters:
        query = session.query(GameModel).filter(*filters)
    else:
        query = session.query(GameModel)
    game_models: List[GameModel] = query.all()
    games = [Game.model_validate(game_model) for game_model in game_models]

    return games


def get_games_to_check_state(session) -> List[RiotGameID]:
    sql_query = """
        SELECT games.id
        FROM games
        JOIN matches ON games.match_id = matches.id
        WHERE matches.start_time < strftime('%Y-%m-%dT%H:%M:%SZ', 'now', 'utc')
        AND games.state != 'COMPLETED' AND games.state != 'UNNEEDED'
    """
    result = session.execute(text(sql_query))
    rows = result.fetchall()
    game_ids = [RiotGameID(row[0]) for row in rows]
    return game_ids


def get_game_by_id(session, game_id: RiotGameID) -> Optional[Game]:
    game_model: GameModel = session.query(GameModel).filter(GameModel.id == game_id).first()
    if game_model is None:
        return None
    else:
        return Game.model_validate(game_model)
