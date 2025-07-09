import logging

from src.common.schemas.riot_data_schemas import League
from src.db.database_service import DatabaseService
from src.riot_scraper.riot_api.riot_api_client import RiotApiClient
from src.riot_scraper.job_runner import JobRunner

logger = logging.getLogger('scraper')


class RiotLeagueScraper:
    def __init__(
            self,
            database_service: DatabaseService,
            riot_api_requester: RiotApiClient,
            job_runner: JobRunner
    ):
        self.db = database_service
        self.riot_api_requester = riot_api_requester
        self.job_runner = job_runner

    def fetch_leagues_from_riot_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.fetch_leagues_from_riot_job,
            job_name="Fetch leagues from riot job",
            max_retries=3
        )

    def fetch_leagues_from_riot_job(self):
        get_leagues_response = self.riot_api_requester.get_leagues()

        for league in get_leagues_response.data.leagues:
            new_league = League(
                id=league.id,
                slug=league.slug,
                name=league.slug,
                region=league.region,
                image=league.image,
                priority=league.displayPriority.position
            )
            self.db.put_league(new_league)
