from src.common.schemas.riot_data_schemas import GameMetadata, RiotGameID
from src.db.models import GameMetadataModel


def put_game_metadata(session, metadata: GameMetadata) -> None:
    session.merge(GameMetadataModel(**metadata.model_dump()))
    session.commit()


def get_game_metadata(session, game_id: RiotGameID) -> GameMetadata | None:
    row = session.query(GameMetadataModel).filter(GameMetadataModel.game_id == game_id).first()
    if row is None:
        return None
    return GameMetadata.model_validate(row)
