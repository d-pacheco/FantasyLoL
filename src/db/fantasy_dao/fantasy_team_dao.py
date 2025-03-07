from src.common.schemas.fantasy_schemas import FantasyLeagueID, FantasyTeam, UserID
from src.db.models import FantasyTeamModel


def put_fantasy_team(session, fantasy_team: FantasyTeam) -> None:
    db_fantasy_team = FantasyTeamModel(**fantasy_team.model_dump())
    session.merge(db_fantasy_team)
    session.commit()


def get_all_fantasy_teams_for_user(
        session,
        fantasy_league_id: FantasyLeagueID,
        user_id: UserID
) -> list[FantasyTeam]:
    db_fantasy_teams: list[FantasyTeamModel] = session.query(FantasyTeamModel)\
        .filter(FantasyTeamModel.fantasy_league_id == fantasy_league_id,
                FantasyTeamModel.user_id == user_id)\
        .all()
    fantasy_teams = [FantasyTeam.model_validate(db_fantasy_team)
                     for db_fantasy_team in db_fantasy_teams]
    return fantasy_teams


def get_all_fantasy_teams_for_week(
        session,
        fantasy_league_id: FantasyLeagueID,
        week: int
) -> list[FantasyTeam]:
    db_fantasy_teams: list[FantasyTeamModel] = session.query(FantasyTeamModel)\
        .filter(FantasyTeamModel.fantasy_league_id == fantasy_league_id,
                FantasyTeamModel.week == week)\
        .all()
    fantasy_teams = [FantasyTeam.model_validate(db_fantasy_team)
                     for db_fantasy_team in db_fantasy_teams]
    return fantasy_teams
