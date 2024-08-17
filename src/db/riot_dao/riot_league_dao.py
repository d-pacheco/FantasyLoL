from sqlalchemy import text
from typing import Optional, List

from src.common.schemas.riot_data_schemas import (
    League,
    RiotLeagueID,
    ProPlayerID
)
from src.db.models import LeagueModel


def put_league(session, league: League) -> None:
    db_league = LeagueModel(**league.model_dump())
    session.merge(db_league)
    session.commit()


def get_leagues(session, filters: Optional[list] = None) -> List[League]:
    if filters:
        query = session.query(LeagueModel).filter(*filters)
    else:
        query = session.query(LeagueModel)
    league_models = query.all()
    leagues = [League.model_validate(league_model) for league_model in league_models]

    return leagues


def get_league_by_id(session, league_id: RiotLeagueID) -> Optional[League]:
    db_league = session.query(LeagueModel).filter(LeagueModel.id == league_id).first()
    if db_league is None:
        return None
    else:
        return League.model_validate(db_league)


def update_league_fantasy_available_status(
        session, league_id: RiotLeagueID, new_status: bool
) -> Optional[League]:
    db_league: Optional[LeagueModel] = session.query(LeagueModel) \
        .filter(LeagueModel.id == league_id).first()
    if db_league is None:
        return None
    db_league.fantasy_available = new_status
    session.merge(db_league)
    session.commit()
    session.refresh(db_league)

    league = League.model_validate(db_league)
    return league


def get_league_ids_for_player(session, player_id: ProPlayerID) -> List[RiotLeagueID]:
    sql_query = f"""
        SELECT DISTINCT l.id
        FROM professional_players p
        JOIN professional_teams t ON p.team_id = t.id
        JOIN leagues l ON t.home_league = l.name
        WHERE p.id = '{player_id}'
        """
    result = session.execute(text(sql_query))
    rows = result.fetchall()
    league_ids = [RiotLeagueID(row[0]) for row in rows]
    return league_ids
