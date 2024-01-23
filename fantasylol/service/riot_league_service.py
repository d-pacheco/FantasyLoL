import logging
from typing import List

from fantasylol.schemas import riot_data_schemas as schemas
from fantasylol.db import crud
from fantasylol.db.models import LeagueModel
from fantasylol.exceptions.league_not_found_exception import LeagueNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.util.job_runner import JobRunner
from fantasylol.schemas.search_parameters import LeagueSearchParameters

logger = logging.getLogger('fantasy-lol')


class RiotLeagueService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()
        self.job_runner = JobRunner()

    def fetch_leagues_from_riot_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.fetch_leagues_from_riot_job,
            job_name="Fetch leagues from riot job",
            max_retries=3
        )

    def fetch_leagues_from_riot_job(self):
        logger.info("Fetching and storing leagues from riot's api")
        fetched_leagues = self.riot_api_requester.get_leagues()
        for league in fetched_leagues:
            crud.save_league(league)

    @staticmethod
    def get_leagues(search_parameters: LeagueSearchParameters) -> List[schemas.League]:
        filters = []
        if search_parameters.name is not None:
            filters.append(LeagueModel.name == search_parameters.name)
        if search_parameters.region is not None:
            filters.append(LeagueModel.region == search_parameters.region)
        orm_leagues = crud.get_leagues(filters)
        leagues = [schemas.League.model_validate(league_orm) for league_orm in orm_leagues]
        return leagues

    @staticmethod
    def get_league_by_id(league_id: str) -> schemas.League:
        league_orm = crud.get_league_by_id(league_id)
        if league_orm is None:
            raise LeagueNotFoundException()
        league = schemas.League.model_validate(league_orm)
        return league
