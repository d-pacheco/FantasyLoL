from src.common.schemas.riot_data_schemas import GameParticipantPerks, RiotGameID
from src.db.models import GameParticipantPerksModel


def put_game_participant_perks(session, perks: GameParticipantPerks) -> None:
    session.merge(GameParticipantPerksModel(**perks.model_dump()))
    session.commit()


def get_game_participant_perks(
    session, game_id: RiotGameID, participant_id: int
) -> GameParticipantPerks | None:
    row = (
        session.query(GameParticipantPerksModel)
        .filter(
            GameParticipantPerksModel.game_id == game_id,
            GameParticipantPerksModel.participant_id == participant_id,
        )
        .first()
    )
    if row is None:
        return None
    return GameParticipantPerks.model_validate(row)
