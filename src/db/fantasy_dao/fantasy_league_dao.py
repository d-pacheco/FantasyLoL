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
        session, fantasy_league_id: FantasyLeagueID
) -> Optional[FantasyLeague]:
    fantasy_league_model: Optional[FantasyLeagueModel] = session.query(FantasyLeagueModel) \
        .filter(FantasyLeagueModel.id == fantasy_league_id).first()
    if fantasy_league_model is None:
        return None
    else:
        return FantasyLeague.model_validate(fantasy_league_model)


def put_fantasy_league_scoring_settings(
        session, scoring_settings: FantasyLeagueScoringSettings
) -> None:
    db_scoring_settings = FantasyLeagueScoringSettingModel(**scoring_settings.model_dump())
    session.merge(db_scoring_settings)
    session.commit()


def get_fantasy_league_scoring_settings_by_id(
        session, fantasy_league_id: FantasyLeagueID
) -> Optional[FantasyLeagueScoringSettings]:
    scoring_settings_model: Optional[FantasyLeagueScoringSettingModel] = session.query(
        FantasyLeagueScoringSettingModel) \
        .filter(FantasyLeagueScoringSettingModel.fantasy_league_id == fantasy_league_id) \
        .first()
    if scoring_settings_model is None:
        return None
    else:
        return FantasyLeagueScoringSettings.model_validate(scoring_settings_model)


def update_fantasy_league_settings(
        session,
        fantasy_league_id: FantasyLeagueID,
        settings: FantasyLeagueSettings
) -> FantasyLeague:
    fantasy_league_model: Optional[FantasyLeagueModel] = session.query(FantasyLeagueModel) \
        .filter_by(id=fantasy_league_id).first()
    assert (fantasy_league_model is not None)

    fantasy_league_model.name = settings.name
    fantasy_league_model.number_of_teams = settings.number_of_teams
    fantasy_league_model.available_leagues = settings.available_leagues

    session.commit()
    session.refresh(fantasy_league_model)
    return FantasyLeague.model_validate(fantasy_league_model)


def update_fantasy_league_status(
        session,
        fantasy_league_id: FantasyLeagueID,
        new_status: FantasyLeagueStatus
) -> FantasyLeague:
    fantasy_league_model: Optional[FantasyLeagueModel] = session.query(FantasyLeagueModel) \
        .filter_by(id=fantasy_league_id).first()
    assert (fantasy_league_model is not None)

    fantasy_league_model.status = new_status
    session.commit()
    session.refresh(fantasy_league_model)
    return FantasyLeague.model_validate(fantasy_league_model)


def update_fantasy_league_current_draft_position(
        session, fantasy_league_id: FantasyLeagueID, new_current_draft_position: int
) -> FantasyLeague:
    fantasy_league_model: Optional[FantasyLeagueModel] = session.query(FantasyLeagueModel) \
        .filter_by(id=fantasy_league_id).first()
    assert (fantasy_league_model is not None)

    fantasy_league_model.current_draft_position = new_current_draft_position
    session.commit()
    session.refresh(fantasy_league_model)
    return FantasyLeague.model_validate(fantasy_league_model)
