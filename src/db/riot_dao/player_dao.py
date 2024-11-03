from typing import Optional, List

from src.common.schemas.riot_data_schemas import ProfessionalPlayer, ProPlayerID
from src.db.models import ProfessionalPlayerModel


def put_player(session, player: ProfessionalPlayer) -> None:
    db_player = ProfessionalPlayerModel(**player.model_dump())
    session.merge(db_player)
    session.commit()


def get_players(session, filters: Optional[list] = None) -> List[ProfessionalPlayer]:
    if filters:
        query = session.query(ProfessionalPlayerModel).filter(*filters)
    else:
        query = session.query(ProfessionalPlayerModel)
    db_players: List[ProfessionalPlayer] = query.all()
    players = [ProfessionalPlayer.model_validate(player_model) for player_model in db_players]
    return players


def get_player_by_id(session, player_id: ProPlayerID) -> Optional[ProfessionalPlayer]:
    db_player: Optional[ProfessionalPlayerModel] = session.query(ProfessionalPlayerModel)\
        .filter(ProfessionalPlayerModel.id == player_id)\
        .first()
    if db_player is None:
        return None
    else:
        return ProfessionalPlayer.model_validate(db_player)
