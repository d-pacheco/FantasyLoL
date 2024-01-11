import logging
from typing import List
from fantasylol.db import crud
from fantasylol.db.models import ProfessionalTeam
from fantasylol.exceptions.professional_team_not_found_exception import \
    ProfessionalTeamNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.schemas.search_parameters import TeamSearchParameters
from fantasylol.schemas.riot_data_schemas import ProfessionalTeamSchema

logger = logging.getLogger('fantasy-lol')


class RiotProfessionalTeamService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_professional_teams(self) -> List[ProfessionalTeamSchema]:
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
            filters.append(ProfessionalTeam.slug == search_parameters.slug)
        if search_parameters.name is not None:
            filters.append(ProfessionalTeam.name == search_parameters.name)
        if search_parameters.code is not None:
            filters.append(ProfessionalTeam.code == search_parameters.code)
        if search_parameters.status is not None:
            filters.append(ProfessionalTeam.status == search_parameters.status)
        if search_parameters.league is not None:
            filters.append(ProfessionalTeam.home_league == search_parameters.league)

        professional_teams = crud.get_teams(filters)
        return professional_teams

    @staticmethod
    def get_team_by_id(professional_team_id: int) -> ProfessionalTeam:
        professional_team = crud.get_team_by_id(professional_team_id)
        if professional_team is None:
            raise ProfessionalTeamNotFoundException()
        return professional_team
