from sqlalchemy import and_
from typing import Optional, List

from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueID,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    UserID
)
from src.db.models import FantasyLeagueModel, FantasyLeagueMembershipModel


def create_fantasy_league_membership(
        session,
        fantasy_league_membership: FantasyLeagueMembership
) -> None:
    db_fantasy_league_membership = FantasyLeagueMembershipModel(
        **fantasy_league_membership.model_dump()
    )
    session.add(db_fantasy_league_membership)
    session.commit()


def get_pending_and_accepted_members_for_league(
        session,
        fantasy_league_id: FantasyLeagueID
) -> List[FantasyLeagueMembership]:
    membership_models = session \
        .query(FantasyLeagueMembershipModel). \
        filter(and_(FantasyLeagueMembershipModel.league_id == fantasy_league_id,
                    FantasyLeagueMembershipModel.status.in_(
                        [FantasyLeagueMembershipStatus.PENDING,
                         FantasyLeagueMembershipStatus.ACCEPTED]))
               ).all()
    memberships = [FantasyLeagueMembership.model_validate(membership_model)
                   for membership_model in membership_models]
    return memberships


def update_fantasy_league_membership_status(
        session,
        membership: FantasyLeagueMembership,
        new_status: FantasyLeagueMembershipStatus
) -> None:
    membership.status = new_status
    db_membership = FantasyLeagueMembershipModel(**membership.model_dump())
    session.merge(db_membership)
    session.commit()


def get_user_membership_for_fantasy_league(
        session,
        user_id: UserID,
        fantasy_league_id: FantasyLeagueID
) -> Optional[FantasyLeagueMembership]:
    membership_model = session.query(FantasyLeagueMembershipModel) \
        .filter(FantasyLeagueMembershipModel.league_id == fantasy_league_id,
                FantasyLeagueMembershipModel.user_id == user_id).first()
    if membership_model is None:
        return None
    else:
        return FantasyLeagueMembership.model_validate(membership_model)


def get_users_fantasy_leagues_with_membership_status(
        session,
        user_id: UserID,
        membership_status: FantasyLeagueMembershipStatus
) -> List[FantasyLeague]:
    fantasy_league_models = session.query(FantasyLeagueModel) \
        .join(FantasyLeagueMembershipModel,
              FantasyLeagueModel.id == FantasyLeagueMembershipModel.league_id) \
        .filter(and_(
            FantasyLeagueMembershipModel.user_id == user_id,
            FantasyLeagueMembershipModel.status == membership_status
        )).all()
    fantasy_leagues = [FantasyLeague.model_validate(fantasy_league_model)
                       for fantasy_league_model in fantasy_league_models]
    return fantasy_leagues
