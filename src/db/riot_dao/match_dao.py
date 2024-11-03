from sqlalchemy import text
from typing import Optional, List

from src.common.schemas.riot_data_schemas import Match, RiotMatchID
from src.db.models import MatchModel


def put_match(session, match: Match) -> None:
    db_match = MatchModel(**match.model_dump())
    session.merge(db_match)
    session.commit()


def get_matches(session, filters: Optional[list] = None) -> List[Match]:
    if filters:
        query = session.query(MatchModel).filter(*filters)
    else:
        query = session.query(MatchModel)
    match_models: List[MatchModel] = query.all()
    matches = [Match.model_validate(match_model) for match_model in match_models]

    return matches


def get_match_by_id(session, match_id: RiotMatchID) -> Optional[Match]:
    db_match: Optional[MatchModel] = session.query(MatchModel).filter(
        MatchModel.id == match_id
    ).first()
    if db_match is None:
        return None
    else:
        return Match.model_validate(db_match)


def get_match_ids_without_games(session) -> List[RiotMatchID]:
    sql_query = """
        SELECT matches.id
        FROM matches
        LEFT JOIN games ON matches.id = games.match_id
        WHERE games.match_id IS NULL AND matches.has_games = True;
    """
    result = session.execute(text(sql_query))
    rows = result.fetchall()
    match_ids = [RiotMatchID(row[0]) for row in rows]
    return match_ids


def update_match_has_games(session, match_id: RiotMatchID, new_has_games: bool) -> None:
    db_match: Optional[MatchModel] = session.query(MatchModel).filter(
        MatchModel.id == match_id
    ).first()
    assert (db_match is not None)
    db_match.has_games = new_has_games
    session.merge(db_match)
    session.commit()
