import logging

from sqlalchemy import or_

from src.common.schemas.search_parameters import TeamSearchParameters
from src.common.schemas.riot_data_schemas import ProfessionalTeam, ProTeamID
from src.db.database_service import DatabaseService
from src.db.models import ProfessionalTeamModel, LeagueModel
from src.riot.exceptions import ProfessionalTeamNotFoundException

logger = logging.getLogger("api.riot")


class RiotProfessionalTeamService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_teams(self, search_parameters: TeamSearchParameters) -> list[ProfessionalTeam]:
        filters: list = []
        join_league = False

        if search_parameters.search is not None:
            term = f"%{search_parameters.search}%"
            filters.append(
                or_(
                    ProfessionalTeamModel.name.ilike(term),
                    ProfessionalTeamModel.code.ilike(term),
                )
            )
        if search_parameters.slug is not None:
            filters.append(ProfessionalTeamModel.slug == search_parameters.slug)
        if search_parameters.name is not None:
            filters.append(ProfessionalTeamModel.name.ilike(f"%{search_parameters.name}%"))
        if search_parameters.code is not None:
            filters.append(ProfessionalTeamModel.code.ilike(f"%{search_parameters.code}%"))
        if search_parameters.status is not None:
            filters.append(ProfessionalTeamModel.status == search_parameters.status)
        if search_parameters.league is not None:
            filters.append(
                ProfessionalTeamModel.home_league_name.ilike(f"%{search_parameters.league}%")
            )
        if search_parameters.fantasy_available is not None:
            join_league = True
            filters.append(LeagueModel.fantasy_available == search_parameters.fantasy_available)
        if search_parameters.active_only:
            filters.append(ProfessionalTeamModel.status == "active")

        return self.db.get_teams(filters, join_league=join_league)

    def get_team_by_id(self, professional_team_id: ProTeamID) -> ProfessionalTeam:
        professional_team = self.db.get_team_by_id(professional_team_id)
        if professional_team is None:
            raise ProfessionalTeamNotFoundException()
        return professional_team
