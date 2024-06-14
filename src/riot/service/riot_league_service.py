import logging
from typing import List

from ...common.exceptions.league_not_found_exception import LeagueNotFoundException
from ...common.schemas.riot_data_schemas import League, RiotLeagueID
from ...common.schemas.search_parameters import LeagueSearchParameters

from ...db import crud
from ...db.models import LeagueModel

from ..util.riot_api_requester import RiotApiRequester
from ..util.job_runner import JobRunner

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
        fetched_leagues = self.riot_api_requester.get_leagues()
        for league in fetched_leagues:
            crud.put_league(league)

    @staticmethod
    def get_leagues(search_parameters: LeagueSearchParameters) -> List[League]:
        filters = []
        if search_parameters.name is not None:
            filters.append(LeagueModel.name == search_parameters.name)
        if search_parameters.region is not None:
            filters.append(LeagueModel.region == search_parameters.region)
        if search_parameters.fantasy_available is not None:
            filters.append(LeagueModel.fantasy_available == search_parameters.fantasy_available)
        leagues = crud.get_leagues(filters)

        return leagues

    @staticmethod
    def get_league_by_id(league_id: RiotLeagueID) -> League:
        league = crud.get_league_by_id(league_id)
        if league is None:
            raise LeagueNotFoundException()
        return league

    @staticmethod
    def update_fantasy_available(league_id: RiotLeagueID, status: bool) -> League:
        league = crud.update_league_fantasy_available_status(league_id, status)
        if league is None:
            raise LeagueNotFoundException()
        return league
