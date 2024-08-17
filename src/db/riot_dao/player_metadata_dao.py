from sqlalchemy import text
from typing import Optional, List

from src.common.schemas.riot_data_schemas import ProPlayerID, RiotGameID, PlayerGameMetadata
from src.db.models import PlayerGameMetadataModel


def put_player_metadata(session, player_metadata: PlayerGameMetadata) -> None:
    db_player_metadata = PlayerGameMetadataModel(**player_metadata.model_dump())
    session.merge(db_player_metadata)
    session.commit()


def get_player_metadata(
        session, player_id: ProPlayerID, game_id: RiotGameID
) -> Optional[PlayerGameMetadata]:
    player_metadata = session.query(PlayerGameMetadataModel) \
        .filter(PlayerGameMetadataModel.player_id == player_id,
                PlayerGameMetadataModel.game_id == game_id).first()
    if player_metadata is None:
        return None
    else:
        return PlayerGameMetadata.model_validate(player_metadata)


def get_game_ids_without_player_metadata(session) -> List[RiotGameID]:
    sql_query = """
        SELECT games.id as game_id
        FROM games
        LEFT JOIN player_game_metadata ON games.id = player_game_metadata.game_id
        WHERE games.state in ('COMPLETED', 'INPROGRESS')
            AND (games.has_game_data = True)
        GROUP BY games.id
        HAVING COUNT(player_game_metadata.game_id) <> 10
        OR COUNT(player_game_metadata.game_id) IS NULL;
    """
    result = session.execute(text(sql_query))
    rows = result.fetchall()
    game_ids = [RiotGameID(row[0]) for row in rows]
    return game_ids
