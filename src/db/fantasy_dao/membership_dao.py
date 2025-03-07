from sqlalchemy import and_

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
    db_membership = FantasyLeagueMembershipModel(
        **fantasy_league_membership.model_dump()
    )
    session.add(db_membership)
    session.commit()


def get_pending_and_accepted_members_for_league(
        session,
        fantasy_league_id: FantasyLeagueID
) -> list[FantasyLeagueMembership]:
    db_memberships: list[FantasyLeagueMembershipModel] = session\
        .query(FantasyLeagueMembershipModel)\
        .filter(and_(FantasyLeagueMembershipModel.league_id == fantasy_league_id,
                     FantasyLeagueMembershipModel.status.in_(
                         [
                             FantasyLeagueMembershipStatus.PENDING,
                             FantasyLeagueMembershipStatus.ACCEPTED
                         ]))
                ).all()
    memberships = [FantasyLeagueMembership.model_validate(db_membership)
                   for db_membership in db_memberships]
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
) -> FantasyLeagueMembership | None:
    db_membership: FantasyLeagueMembershipModel | None = session\
        .query(FantasyLeagueMembershipModel)\
        .filter(FantasyLeagueMembershipModel.league_id == fantasy_league_id,
                FantasyLeagueMembershipModel.user_id == user_id).first()
    if db_membership is None:
        return None
    else:
        return FantasyLeagueMembership.model_validate(db_membership)


def get_users_fantasy_leagues_with_membership_status(
        session,
        user_id: UserID,
        membership_status: FantasyLeagueMembershipStatus
) -> list[FantasyLeague]:
    db_fantasy_leagues: list[FantasyLeagueModel] = session.query(FantasyLeagueModel)\
        .join(FantasyLeagueMembershipModel,
              FantasyLeagueModel.id == FantasyLeagueMembershipModel.league_id)\
        .filter(and_(
            FantasyLeagueMembershipModel.user_id == user_id,
            FantasyLeagueMembershipModel.status == membership_status
        )).all()
    fantasy_leagues = [FantasyLeague.model_validate(db_fantasy_league)
                       for db_fantasy_league in db_fantasy_leagues]
    return fantasy_leagues
