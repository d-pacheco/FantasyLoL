from typing import Optional, List

from src.common.schemas.riot_data_schemas import ProfessionalTeam, ProTeamID
from src.db.models import ProfessionalTeamModel


def put_team(session, team: ProfessionalTeam) -> None:
    db_team = ProfessionalTeamModel(**team.model_dump())
    session.merge(db_team)
    session.commit()


def get_teams(session, filters: Optional[list] = None) -> List[ProfessionalTeam]:
    if filters:
        query = session.query(ProfessionalTeamModel).filter(*filters)
    else:
        query = session.query(ProfessionalTeamModel)
    db_teams: List[ProfessionalTeamModel] = query.all()
    teams = [ProfessionalTeam.model_validate(db_team) for db_team in db_teams]

    return teams


def get_team_by_id(session, team_id: ProTeamID) -> Optional[ProfessionalTeam]:
    db_team: Optional[ProfessionalTeamModel] = session.query(ProfessionalTeamModel)\
        .filter(ProfessionalTeamModel.id == team_id)\
        .first()
    if db_team is None:
        return None
    else:
        return ProfessionalTeam.model_validate(db_team)
