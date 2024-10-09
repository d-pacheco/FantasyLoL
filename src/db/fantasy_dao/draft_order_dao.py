from typing import List

from src.common.schemas.fantasy_schemas import FantasyLeagueID, FantasyLeagueDraftOrder
from src.db.models import FantasyLeagueDraftOrderModel


def create_fantasy_league_draft_order(session, draft_order: FantasyLeagueDraftOrder) -> None:
    db_draft_order = FantasyLeagueDraftOrderModel(**draft_order.model_dump())
    session.add(db_draft_order)
    session.commit()


def get_fantasy_league_draft_order(
        session, fantasy_league_id: FantasyLeagueID
) -> List[FantasyLeagueDraftOrder]:
    draft_order_models = session \
        .query(FantasyLeagueDraftOrderModel) \
        .filter(FantasyLeagueDraftOrderModel.fantasy_league_id == fantasy_league_id) \
        .all()
    draft_orders = [FantasyLeagueDraftOrder.model_validate(draft_order_model)
                    for draft_order_model in draft_order_models]
    return draft_orders


def delete_fantasy_league_draft_order(session, draft_order: FantasyLeagueDraftOrder) -> None:
    db_draft_order = session.query(FantasyLeagueDraftOrderModel) \
        .filter(FantasyLeagueDraftOrderModel.fantasy_league_id == draft_order.fantasy_league_id,
                FantasyLeagueDraftOrderModel.user_id == draft_order.user_id).first()
    assert (db_draft_order is not None)
    session.delete(db_draft_order)
    session.commit()


def update_fantasy_league_draft_order_position(
        session,
        draft_order: FantasyLeagueDraftOrder,
        new_position: int) -> None:
    draft_order.position = new_position
    db_draft_order = FantasyLeagueDraftOrderModel(**draft_order.model_dump())
    session.merge(db_draft_order)
    session.commit()