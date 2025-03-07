from sqlalchemy import text

from src.common.schemas.riot_data_schemas import RiotGameID, PlayerGameData, PlayerGameStats
from src.db.models import PlayerGameStatsModel
from src.db.views import PlayerGameView


def put_player_stats(session, player_stats: PlayerGameStats) -> None:
    db_player_stats = PlayerGameStatsModel(**player_stats.model_dump())
    session.merge(db_player_stats)
    session.commit()


def get_player_stats(
        session,
        game_id: RiotGameID,
        participant_id: int
) -> PlayerGameStats | None:
    db_player_game_stats: PlayerGameStatsModel | None = session.query(PlayerGameStatsModel)\
        .filter(PlayerGameStatsModel.game_id == game_id,
                PlayerGameStatsModel.participant_id == participant_id).first()
    if db_player_game_stats is None:
        return None
    else:
        return PlayerGameStats.model_validate(db_player_game_stats)


def get_game_ids_to_fetch_player_stats_for(session) -> list[RiotGameID]:
    sql_query = """
        SELECT games.id as game_id
        FROM games
        LEFT JOIN player_game_stats ON games.id = player_game_stats.game_id
        WHERE ((games.state = 'COMPLETED'
                AND (SELECT COUNT(*) FROM player_game_stats WHERE game_id = games.id) < 10)
                OR games.state = 'INPROGRESS')
            AND (games.has_game_data = True)
        GROUP BY games.id
    """
    result = session.execute(text(sql_query))
    rows = result.fetchall()
    game_ids = [RiotGameID(row[0]) for row in rows]
    return game_ids


def get_player_game_stats(session, filters: list | None = None) -> list[PlayerGameData]:
    if filters:
        query = session.query(PlayerGameView).filter(*filters)
    else:
        query = session.query(PlayerGameView)

    db_player_game_stat: list[PlayerGameView] = query.all()
    player_game_data = [PlayerGameData.model_validate(db_player_game_stat)
                        for db_player_game_stat in db_player_game_stat]
    return player_game_data
