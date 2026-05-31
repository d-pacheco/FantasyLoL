from src.common.schemas.fantasy_schemas import FantasyLeagueID, DraftPick
from src.db.models import DraftPickModel


def put_draft_pick(session, draft_pick: DraftPick) -> None:
    db_draft_pick = DraftPickModel(**draft_pick.model_dump())
    session.merge(db_draft_pick)
    session.commit()


def get_draft_picks_for_league(session, fantasy_league_id: FantasyLeagueID) -> list[DraftPick]:
    db_draft_picks: list[DraftPickModel] = (
        session.query(DraftPickModel)
        .filter(DraftPickModel.fantasy_league_id == fantasy_league_id)
        .order_by(DraftPickModel.pick_number)
        .all()
    )
    return [DraftPick.model_validate(dp) for dp in db_draft_picks]
