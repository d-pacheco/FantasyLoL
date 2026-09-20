from sqlalchemy import text

from src.common.schemas.riot_data_schemas import TeamGameStats, ProTeamID
from src.db.models import TeamGameStatsModel


def put_team_stats(session, team_stats: TeamGameStats):
    db_team_stats = TeamGameStatsModel(**team_stats.model_dump())
    session.merge(db_team_stats)
    session.commit()


# Per-game team stat lines with the team's dragon count for each game.
_TEAM_STAT_LINES_SQL = text("""
    SELECT
        tgs.game_id,
        tgs.total_kills,
        tgs.total_gold,
        tgs.towers,
        tgs.barons,
        tgs.inhibitors,
        COALESCE(d.dragon_count, 0) AS dragons
    FROM team_game_stats tgs
    LEFT JOIN (
        SELECT game_id, team_id, COUNT(*) AS dragon_count
        FROM game_dragons
        GROUP BY game_id, team_id
    ) d ON d.game_id = tgs.game_id AND d.team_id = tgs.team_id
    WHERE tgs.team_id = :team_id
""")


def get_team_game_stat_lines(session, team_id: ProTeamID) -> list[dict]:
    rows = session.execute(_TEAM_STAT_LINES_SQL, {"team_id": team_id}).mappings().all()
    return [
        {
            "game_id": r["game_id"],
            "total_kills": r["total_kills"] or 0,
            "total_gold": r["total_gold"] or 0,
            "towers": r["towers"] or 0,
            "barons": r["barons"] or 0,
            "inhibitors": r["inhibitors"] or 0,
            "dragons": r["dragons"] or 0,
        }
        for r in rows
    ]
