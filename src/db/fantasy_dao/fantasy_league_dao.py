from typing import Optional

from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueID,
    FantasyLeagueScoringSettings,
    FantasyLeagueStatus,
    FantasyLeagueSettings,
)
from src.db.models import FantasyLeagueScoringSettingModel, FantasyLeagueModel


def create_fantasy_league(session, fantasy_league: FantasyLeague) -> None:
    db_fantasy_league = FantasyLeagueModel(**fantasy_league.model_dump())
    session.add(db_fantasy_league)
    session.commit()


def get_fantasy_league_by_id(
        session,
        fantasy_league_id: FantasyLeagueID
) -> Optional[FantasyLeague]:
    db_fantasy_league: Optional[FantasyLeagueModel] = session.query(FantasyLeagueModel) \
        .filter(FantasyLeagueModel.id == fantasy_league_id).first()
    if db_fantasy_league is None:
        return None
    else:
        return FantasyLeague.model_validate(db_fantasy_league)


def put_fantasy_league_scoring_settings(
        session,
        scoring_settings: FantasyLeagueScoringSettings
) -> None:
    db_scoring_settings = FantasyLeagueScoringSettingModel(**scoring_settings.model_dump())
    session.merge(db_scoring_settings)
    session.commit()


def get_fantasy_league_scoring_settings_by_id(
        session,
        fantasy_league_id: FantasyLeagueID
) -> Optional[FantasyLeagueScoringSettings]:
    db_scoring_setting: Optional[FantasyLeagueScoringSettingModel] = session\
        .query(FantasyLeagueScoringSettingModel)\
        .filter(FantasyLeagueScoringSettingModel.fantasy_league_id == fantasy_league_id)\
        .first()
    if db_scoring_setting is None:
        return None
    else:
        return FantasyLeagueScoringSettings.model_validate(db_scoring_setting)


def update_fantasy_league_settings(
        session,
        fantasy_league_id: FantasyLeagueID,
        settings: FantasyLeagueSettings
) -> FantasyLeague:
    db_fantasy_league: Optional[FantasyLeagueModel] = session.query(FantasyLeagueModel)\
        .filter_by(id=fantasy_league_id)\
        .first()
    assert (db_fantasy_league is not None)

    db_fantasy_league.name = settings.name
    db_fantasy_league.number_of_teams = settings.number_of_teams
    db_fantasy_league.available_leagues = settings.available_leagues

    session.commit()
    session.refresh(db_fantasy_league)
    return FantasyLeague.model_validate(db_fantasy_league)


def update_fantasy_league_status(
        session,
        fantasy_league_id: FantasyLeagueID,
        new_status: FantasyLeagueStatus
) -> FantasyLeague:
    db_fantasy_league: Optional[FantasyLeagueModel] = session.query(FantasyLeagueModel)\
        .filter_by(id=fantasy_league_id)\
        .first()
    assert (db_fantasy_league is not None)

    db_fantasy_league.status = new_status
    session.commit()
    session.refresh(db_fantasy_league)
    return FantasyLeague.model_validate(db_fantasy_league)


def update_fantasy_league_current_draft_position(
        session,
        fantasy_league_id: FantasyLeagueID,
        new_current_draft_position: int
) -> FantasyLeague:
    db_fantasy_league: Optional[FantasyLeagueModel] = session.query(FantasyLeagueModel)\
        .filter_by(id=fantasy_league_id)\
        .first()
    assert (db_fantasy_league is not None)

    db_fantasy_league.current_draft_position = new_current_draft_position
    session.commit()
    session.refresh(db_fantasy_league)
    return FantasyLeague.model_validate(db_fantasy_league)
