from sqlalchemy import and_
from typing import List

from src.db.database import DatabaseConnection
from src.common.schemas import fantasy_schemas
from src.db import models


def get_user_by_username(username: str) -> models.UserModel:
    with DatabaseConnection() as db:
        return db.query(models.UserModel) \
            .filter(models.UserModel.username == username).first()


def create_user(user: fantasy_schemas.User):
    db_user = models.UserModel(**user.model_dump())
    with DatabaseConnection() as db:
        db.add(db_user)
        db.commit()


def create_fantasy_league(fantasy_league: fantasy_schemas.FantasyLeague):
    db_fantasy_league = models.FantasyLeagueModel(**fantasy_league.model_dump())
    with DatabaseConnection() as db:
        db.add(db_fantasy_league)
        db.commit()


def get_fantasy_league_by_id(fantasy_league_id: str) -> models.FantasyLeagueModel:
    with DatabaseConnection() as db:
        return db.query(models.FantasyLeagueModel) \
            .filter(models.FantasyLeagueModel.id == fantasy_league_id).first()


def get_pending_and_accepted_members_for_league(league_id: str) \
        -> List[models.FantasyLeagueMembershipModel]:
    with DatabaseConnection() as db:
        return db.query(models.FantasyLeagueMembershipModel). \
            filter(and_(models.FantasyLeagueMembershipModel.league_id == league_id,
                        models.FantasyLeagueMembershipModel.status.in_(
                            [fantasy_schemas.FantasyLeagueMembershipStatus.PENDING,
                             fantasy_schemas.FantasyLeagueMembershipStatus.ACCEPTED]))
                   ).all()


def get_all_league_memberships(league_id: str) -> List[models.FantasyLeagueMembershipModel]:
    with DatabaseConnection() as db:
        return db.query(models.FantasyLeagueMembershipModel) \
            .filter(models.FantasyLeagueMembershipModel.league_id == league_id).all()


def create_fantasy_league_scoring_settings(
        scoring_settings: fantasy_schemas.FantasyLeagueScoringSettings):
    db_scoring_settings = models.FantasyLeagueScoringSettingModel(**scoring_settings.model_dump())
    with DatabaseConnection() as db:
        db.add(db_scoring_settings)
        db.commit()


def get_fantasy_league_scoring_settings_by_id(league_id: str) \
        -> models.FantasyLeagueScoringSettingModel:
    with DatabaseConnection() as db:
        return db.query(models.FantasyLeagueScoringSettingModel) \
            .filter(models.FantasyLeagueScoringSettingModel.fantasy_league_id == league_id) \
            .first()


def create_fantasy_league_membership(
        fantasy_league_membership: fantasy_schemas.FantasyLeagueMembership):
    db_fantasy_league_membership = models.FantasyLeagueMembershipModel(
        **fantasy_league_membership.model_dump()
    )
    with DatabaseConnection() as db:
        db.merge(db_fantasy_league_membership)
        db.commit()
