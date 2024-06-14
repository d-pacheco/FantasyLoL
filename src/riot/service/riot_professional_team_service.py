import logging
from typing import List

from ...common.schemas.search_parameters import TeamSearchParameters
from ...common.schemas.riot_data_schemas import ProfessionalTeam, ProTeamID

from ...db import crud
from ...db.models import ProfessionalTeamModel

from ..exceptions.professional_team_not_found_exception import \
    ProfessionalTeamNotFoundException
from ..util.riot_api_requester import RiotApiRequester
from ..util.job_runner import JobRunner

logger = logging.getLogger('fantasy-lol')


class RiotProfessionalTeamService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()
        self.job_runner = JobRunner()

    def fetch_professional_teams_from_riot_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.fetch_professional_teams_from_riot_job,
            job_name="fetch teams from riot job",
            max_retries=3
        )

    def fetch_professional_teams_from_riot_job(self):
        fetched_teams = self.riot_api_requester.get_teams()

        for team in fetched_teams:
            crud.put_team(team)
        return fetched_teams

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

        professional_teams = crud.get_teams(filters)
        return professional_teams

    @staticmethod
    def get_team_by_id(professional_team_id: ProTeamID) -> ProfessionalTeam:
        professional_team = crud.get_team_by_id(professional_team_id)
        if professional_team is None:
            raise ProfessionalTeamNotFoundException()
        return professional_team
