import logging

from sqlalchemy import text, select, func, or_, cast, Date

from src.common.schemas.riot_data_schemas import Match, RiotMatchID, RiotLeagueID
from src.db.models import (
    MatchModel,
    EventTeamsModel,
    LeagueModel,
    TournamentModel,
    ProfessionalTeamModel,
)
from src.db.views import MatchView

logger = logging.getLogger("riot")


def _resolve_team_by_name(session, team_name: str):
    return (
        session.query(ProfessionalTeamModel).filter(ProfessionalTeamModel.name == team_name).first()
    )


def put_match(session, match: Match) -> None:
    league = session.query(LeagueModel).filter(LeagueModel.slug == match.league_slug).first()
    league_id = league.id if league else None

    db_match = MatchModel(
        id=match.id,
        start_time=match.start_time,
        block_name=match.block_name,
        league_id=league_id,
        strategy_type=match.strategy_type,
        strategy_count=match.strategy_count,
        tournament_id=match.tournament_id,
        has_games=match.has_games,
        state=match.state,
    )
    session.merge(db_match)
    session.flush()

    winning_team = match.winning_team
    team_1_outcome = (
        "win"
        if winning_team == match.team_1_name
        else ("loss" if winning_team and winning_team != match.team_1_name else None)
    )
    team_2_outcome = (
        "win"
        if winning_team == match.team_2_name
        else ("loss" if winning_team and winning_team != match.team_2_name else None)
    )

    for side, name, game_wins, outcome in [
        (1, match.team_1_name, match.team_1_wins, team_1_outcome),
        (2, match.team_2_name, match.team_2_wins, team_2_outcome),
    ]:
        if not name:
            continue
        team = _resolve_team_by_name(session, name)
        if team is None:
            logger.warning(f"Team '{name}' not found in professional_teams, skipping event_team")
            continue
        et = EventTeamsModel(
            match_id=match.id,
            team_id=team.id,
            side=side,
            team_code=team.code,
            team_name=name,
            team_image=team.image,
            game_wins=game_wins,
            outcome=outcome,
        )
        session.merge(et)

    session.commit()


def get_matches(session, filters: list | None = None) -> list[Match]:
    if filters:
        query = session.query(MatchView).filter(*filters)
    else:
        query = session.query(MatchView)
    match_models = query.all()
    return [Match.model_validate(match_model) for match_model in match_models]


def get_match_by_id(session, match_id: RiotMatchID) -> Match | None:
    db_match = session.query(MatchView).filter(MatchView.id == match_id).first()
    if db_match is None:
        return None
    return Match.model_validate(db_match)


def get_match_ids_without_games(session) -> list[RiotMatchID]:
    sql_query = """
        SELECT matches.id
        FROM matches
        LEFT JOIN games ON matches.id = games.match_id
        WHERE games.match_id IS NULL AND matches.has_games = True;
    """
    result = session.execute(text(sql_query))
    rows = result.fetchall()
    return [RiotMatchID(row[0]) for row in rows]


def update_match_has_games(session, match_id: RiotMatchID, new_has_games: bool) -> None:
    db_match = session.query(MatchModel).filter(MatchModel.id == match_id).first()
    assert db_match is not None
    db_match.has_games = new_has_games
    session.merge(db_match)
    session.commit()


def get_matches_for_league_with_active_tournament(session, league_id: RiotLeagueID) -> list[Match]:
    query = select(MatchView).where(
        MatchView.tournament_id.in_(
            select(TournamentModel.id).where(
                TournamentModel.league_id == league_id,
                func.current_date().between(
                    cast(TournamentModel.start_date, Date),
                    cast(TournamentModel.end_date, Date),
                ),
            )
        ),
        func.substr(MatchView.start_time, 1, 10).between(
            select(TournamentModel.start_date)
            .where(
                TournamentModel.league_id == league_id,
                func.current_date().between(
                    cast(TournamentModel.start_date, Date),
                    cast(TournamentModel.end_date, Date),
                ),
            )
            .correlate(None)
            .scalar_subquery(),
            select(TournamentModel.end_date)
            .where(
                TournamentModel.league_id == league_id,
                func.current_date().between(
                    cast(TournamentModel.start_date, Date),
                    cast(TournamentModel.end_date, Date),
                ),
            )
            .correlate(None)
            .scalar_subquery(),
        ),
    )
    match_models = session.execute(query).scalars().all()
    return [Match.model_validate(match_model) for match_model in match_models]


def get_miss_data_matches(session) -> list[Match]:
    match_models = (
        session.execute(
            select(MatchView).where(
                or_(
                    or_(MatchView.team_1_name == "TBD", MatchView.team_2_name == "TBD"),
                    or_(MatchView.state == "UNSTARTED", MatchView.state == "INPROGRESS"),
                )
            )
        )
        .scalars()
        .all()
    )
    return [Match.model_validate(match_model) for match_model in match_models]
