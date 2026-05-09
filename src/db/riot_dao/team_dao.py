from sqlalchemy import func

from src.common.schemas.riot_data_schemas import ProfessionalTeam, ProTeamID
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
