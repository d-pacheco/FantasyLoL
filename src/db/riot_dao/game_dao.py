import logging

from sqlalchemy import text

from src.common.schemas.riot_data_schemas import Game, RiotGameID, GameState
from src.db.models import GameModel, GameTeamsModel
from src.db.views import GameView

logger = logging.getLogger("riot")


def put_game(session, game: Game) -> None:
    db_game = GameModel(
        id=game.id,
        state=game.state,
        number=game.number,
        match_id=game.match_id,
        details_status="unavailable" if not game.has_game_data else None,
    )
    session.merge(db_game)
    session.flush()

    for team_id, side in [(game.red_team, "red"), (game.blue_team, "blue")]:
        if team_id:
            gt = GameTeamsModel(game_id=game.id, team_id=team_id, side=side)
            session.merge(gt)

    session.commit()


def bulk_save_games(session, games: list[Game]) -> None:
    for game in games:
        put_game(session, game)


def update_has_game_data(session, game_id: RiotGameID, has_game_data: bool) -> None:
    db_game = session.query(GameModel).filter(GameModel.id == game_id).first()
    if db_game is not None:
        db_game.details_status = None if has_game_data else "unavailable"
        session.merge(db_game)
        session.commit()


def update_game_state(session, game_id: RiotGameID, state: GameState) -> None:
    db_game = session.query(GameModel).filter(GameModel.id == game_id).first()
    if db_game is not None:
        db_game.state = state
        session.merge(db_game)
        session.commit()


def update_game_last_stats_fetch(session, game_id: RiotGameID, last_fetch: bool) -> None:
    db_game = session.query(GameModel).filter(GameModel.id == game_id).first()
    if db_game is not None:
        db_game.details_status = "needs_final_fetch" if last_fetch else None
        session.merge(db_game)
        session.commit()


def get_games_with_last_stats_fetch(session, last_stats_fetch: bool) -> list[Game]:
    if last_stats_fetch:
        game_models = (
            session.query(GameView)
            .filter(GameView.last_stats_fetch == True)  # noqa: E712
            .all()
        )
    else:
        game_models = (
            session.query(GameView)
            .filter(GameView.last_stats_fetch == False)  # noqa: E712
            .all()
        )
    return [Game.model_validate(gm) for gm in game_models]


def get_games(session, filters: list | None = None) -> list[Game]:
    if filters:
        query = session.query(GameView).filter(*filters)
    else:
        query = session.query(GameView)
    game_models = query.all()
    return [Game.model_validate(gm) for gm in game_models]


def get_games_to_check_state(session) -> list[RiotGameID]:
    sql_query = """
        SELECT games.id
        FROM games
        JOIN matches ON games.match_id = matches.id
        WHERE matches.start_time < to_char(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
        AND games.state != 'COMPLETED' AND games.state != 'UNNEEDED'
    """
    result = session.execute(text(sql_query))
    rows = result.fetchall()
    return [RiotGameID(row[0]) for row in rows]


def get_game_by_id(session, game_id: RiotGameID) -> Game | None:
    gm = session.query(GameView).filter(GameView.id == game_id).first()
    if gm is None:
        return None
    return Game.model_validate(gm)
