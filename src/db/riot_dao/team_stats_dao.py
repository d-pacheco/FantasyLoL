from src.common.schemas.riot_data_schemas import TeamGameStats
from src.db.models import TeamGameStatsModel


def put_team_stats(session, team_stats: TeamGameStats):
    db_team_stats = TeamGameStatsModel(**team_stats.model_dump())
    session.merge(db_team_stats)
    session.commit()
