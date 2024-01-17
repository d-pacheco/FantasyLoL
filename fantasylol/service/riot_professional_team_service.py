import logging
from typing import List
from fantasylol.db import crud
from fantasylol.db.models import ProfessionalTeamModel
from fantasylol.exceptions.professional_team_not_found_exception import \
    ProfessionalTeamNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.schemas.search_parameters import TeamSearchParameters
from fantasylol.schemas.riot_data_schemas import ProfessionalTeam

logger = logging.getLogger('fantasy-lol')


class RiotProfessionalTeamService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_professional_teams(self) -> List[ProfessionalTeam]:
        logger.info("Fetching and storing professional teams from riot's api")
        try:
            fetched_teams = self.riot_api_requester.get_teams()

            for team in fetched_teams:
                crud.save_team(team)
            return fetched_teams
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise e

    @staticmethod
    def get_teams(search_parameters: TeamSearchParameters) -> List[ProfessionalTeam]:
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

        professional_teams_orms = crud.get_teams(filters)
        professional_teams = [ProfessionalTeam.model_validate(team_orm)
                              for team_orm in professional_teams_orms]
        return professional_teams

    @staticmethod
    def get_team_by_id(professional_team_id: str) -> ProfessionalTeam:
        professional_team_orm = crud.get_team_by_id(professional_team_id)
        if professional_team_orm is None:
            raise ProfessionalTeamNotFoundException()
        professional_team = ProfessionalTeam.model_validate(professional_team_orm)
        return professional_team
