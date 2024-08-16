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
    team_models: List[ProfessionalTeamModel] = query.all()
    teams = [ProfessionalTeam.model_validate(team_model) for team_model in team_models]

    return teams


def get_team_by_id(session, team_id: ProTeamID) -> Optional[ProfessionalTeam]:
    team_model: ProfessionalTeamModel = session.query(ProfessionalTeamModel) \
        .filter(ProfessionalTeamModel.id == team_id).first()
    if team_model is None:
        return None
    else:
        return ProfessionalTeam.model_validate(team_model)
