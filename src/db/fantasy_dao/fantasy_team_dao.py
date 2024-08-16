from typing import List

from src.common.schemas.fantasy_schemas import FantasyLeagueID, FantasyTeam, UserID
from src.db.models import FantasyTeamModel


def put_fantasy_team(session, fantasy_team: FantasyTeam) -> None:
    db_fantasy_team = FantasyTeamModel(**fantasy_team.model_dump())
    session.merge(db_fantasy_team)
    session.commit()


def get_all_fantasy_teams_for_user(
        session, fantasy_league_id: FantasyLeagueID, user_id: UserID
) -> List[FantasyTeam]:
    fantasy_team_models = session.query(FantasyTeamModel) \
        .filter(FantasyTeamModel.fantasy_league_id == fantasy_league_id,
                FantasyTeamModel.user_id == user_id).all()
    fantasy_teams = [FantasyTeam.model_validate(fantasy_team_model)
                     for fantasy_team_model in fantasy_team_models]
    return fantasy_teams


def get_all_fantasy_teams_for_week(
        session, fantasy_league_id: FantasyLeagueID, week: int
) -> List[FantasyTeam]:
    fantasy_team_models = session.query(FantasyTeamModel) \
        .filter(FantasyTeamModel.fantasy_league_id == fantasy_league_id,
                FantasyTeamModel.week == week).all()
    fantasy_teams = [FantasyTeam.model_validate(fantasy_team_model)
                     for fantasy_team_model in fantasy_team_models]
    return fantasy_teams
