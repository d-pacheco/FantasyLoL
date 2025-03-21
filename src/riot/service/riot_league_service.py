import logging

from src.common.exceptions import LeagueNotFoundException
from src.common.schemas.riot_data_schemas import League, RiotLeagueID
from src.common.schemas.search_parameters import LeagueSearchParameters

from src.db.database_service import DatabaseService
from src.db.models import LeagueModel

from src.riot.util import RiotApiRequester
from src.riot.job_runner import JobRunner

logger = logging.getLogger('riot')


class RiotLeagueService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
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
            self.db.put_league(league)

    def get_leagues(self, search_parameters: LeagueSearchParameters) -> list[League]:
        filters = []
        if search_parameters.name is not None:
            filters.append(LeagueModel.name == search_parameters.name)
        if search_parameters.region is not None:
            filters.append(LeagueModel.region == search_parameters.region)
        if search_parameters.fantasy_available is not None:
            filters.append(LeagueModel.fantasy_available == search_parameters.fantasy_available)
        leagues = self.db.get_leagues(filters)

        return leagues

    def get_league_by_id(self, league_id: RiotLeagueID) -> League:
        league = self.db.get_league_by_id(league_id)
        if league is None:
            raise LeagueNotFoundException(league_id)
        return league

    def update_fantasy_available(self, league_id: RiotLeagueID, status: bool) -> League:
        league = self.db.update_league_fantasy_available_status(league_id, status)
        if league is None:
            raise LeagueNotFoundException(league_id)
        return league
