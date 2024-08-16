from sqlalchemy import text
from typing import Optional, List

from src.common.schemas.riot_data_schemas import RiotGameID, PlayerGameData, PlayerGameStats
from src.db.models import PlayerGameStatsModel
from src.db.views import PlayerGameView


def put_player_stats(session, player_stats: PlayerGameStats) -> None:
    db_player_stats = PlayerGameStatsModel(**player_stats.model_dump())
    session.merge(db_player_stats)
    session.commit()


def get_player_stats(session, game_id: RiotGameID, participant_id: int) -> Optional[PlayerGameStats]:
    player_game_stats = session.query(PlayerGameStatsModel) \
        .filter(PlayerGameStatsModel.game_id == game_id,
                PlayerGameStatsModel.participant_id == participant_id).first()
    if player_game_stats is None:
        return None
    else:
        return PlayerGameStats.model_validate(player_game_stats)


def get_game_ids_to_fetch_player_stats_for(session) -> List[RiotGameID]:
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


def get_player_game_stats(session, filters: Optional[list] = None) -> List[PlayerGameData]:
    if filters:
        query = session.query(PlayerGameView).filter(*filters)
    else:
        query = session.query(PlayerGameView)

    player_game_stat_models: List[PlayerGameView] = query.all()
    player_game_data = [PlayerGameData.model_validate(player_game_stat_model)
                        for player_game_stat_model in player_game_stat_models]
    return player_game_data
