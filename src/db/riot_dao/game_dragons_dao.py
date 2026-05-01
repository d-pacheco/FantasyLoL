from src.common.schemas.riot_data_schemas import GameDragons, RiotGameID
from src.db.models import GameDragonsModel


def put_game_dragon(session, dragon: GameDragons) -> None:
    session.merge(GameDragonsModel(**dragon.model_dump()))
    session.commit()


def get_game_dragons(session, game_id: RiotGameID) -> list[GameDragons]:
    rows = session.query(GameDragonsModel).filter(GameDragonsModel.game_id == game_id).all()
    return [GameDragons.model_validate(row) for row in rows]
