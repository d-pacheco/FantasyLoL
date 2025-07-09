import logging

from src.common.schemas.search_parameters import TeamSearchParameters
from src.common.schemas.riot_data_schemas import ProfessionalTeam, ProTeamID

from src.db.database_service import DatabaseService
from src.db.models import ProfessionalTeamModel

from src.riot.exceptions import ProfessionalTeamNotFoundException

logger = logging.getLogger('riot')


class RiotProfessionalTeamService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_teams(self, search_parameters: TeamSearchParameters) -> list[ProfessionalTeam]:
        filters = []
        if search_parameters.slug is not None:
            filters.append(ProfessionalTeamModel.slug == search_parameters.slug)
        if search_parameters.name is not None:
            filters.append(ProfessionalTeamModel.name == search_parameters.name)
        if search_parameters.code is not None:
            filters.append(ProfessionalTeamModel.code == search_parameters.code)
        if search_parameters.status is not None:
            filters.append(ProfessionalTeamModel.status == search_parameters.status)
        if search_parameters.league is not None:
            filters.append(ProfessionalTeamModel.home_league == search_parameters.league)

        professional_teams = self.db.get_teams(filters)
        return professional_teams

    def get_team_by_id(self, professional_team_id: ProTeamID) -> ProfessionalTeam:
        professional_team = self.db.get_team_by_id(professional_team_id)
        if professional_team is None:
            raise ProfessionalTeamNotFoundException()
        return professional_team
