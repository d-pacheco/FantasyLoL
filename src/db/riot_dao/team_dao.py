from sqlalchemy import func, text

from src.common.schemas.riot_data_schemas import (
    ProfessionalTeam,
    ProTeamID,
    TeamMatchHistoryEntry,
)
from src.db.models import ProfessionalTeamModel, LeagueModel


def put_team(session, team: ProfessionalTeam) -> None:
    db_team = ProfessionalTeamModel(**team.model_dump())
    session.merge(db_team)
    session.commit()


def get_teams(
    session, filters: list | None = None, join_league: bool = False
) -> list[ProfessionalTeam]:
    query = session.query(ProfessionalTeamModel)
    if join_league:
        query = query.join(
            LeagueModel,
            func.lower(ProfessionalTeamModel.home_league_name) == func.lower(LeagueModel.name),
        )
    if filters:
        query = query.filter(*filters)
    db_teams = query.all()
    return [ProfessionalTeam.model_validate(db_team) for db_team in db_teams]


def get_team_by_id(session, team_id: ProTeamID) -> ProfessionalTeam | None:
    db_team = (
        session.query(ProfessionalTeamModel).filter(ProfessionalTeamModel.id == team_id).first()
    )
    if db_team is None:
        return None
    return ProfessionalTeam.model_validate(db_team)


# Match-level history for a team. The opponent is the other event_teams row for
# the same match (matched by side, so it is never the team itself).
_TEAM_MATCH_HISTORY_SQL = text("""
    SELECT
        m.id AS match_id,
        m.start_time,
        m.league_slug,
        m.block_name,
        m.strategy_type,
        m.strategy_count,
        opp.team_code AS opponent_code,
        opp.team_name AS opponent_name,
        self.outcome AS outcome,
        self.game_wins AS team_score,
        opp.game_wins AS opponent_score
    FROM event_teams self
    JOIN matches m ON m.id = self.match_id
    LEFT JOIN event_teams opp ON opp.match_id = self.match_id AND opp.side <> self.side
    WHERE self.team_id = :team_id
    ORDER BY m.start_time DESC NULLS LAST, m.id DESC
""")


def get_team_match_history(session, team_id: ProTeamID) -> list[TeamMatchHistoryEntry]:
    rows = session.execute(_TEAM_MATCH_HISTORY_SQL, {"team_id": team_id}).mappings().all()
    history: list[TeamMatchHistoryEntry] = []
    for row in rows:
        outcome = row["outcome"]
        win = None if outcome is None else outcome == "win"
        history.append(
            TeamMatchHistoryEntry(
                match_id=row["match_id"],
                start_time=row["start_time"],
                league_slug=row["league_slug"],
                block_name=row["block_name"],
                strategy_type=row["strategy_type"],
                strategy_count=row["strategy_count"],
                opponent_code=row["opponent_code"],
                opponent_name=row["opponent_name"],
                win=win,
                team_score=row["team_score"],
                opponent_score=row["opponent_score"],
            )
        )
    return history
