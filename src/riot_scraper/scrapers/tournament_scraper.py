import logging

from src.common.schemas.riot_data_schemas import Tournament
from src.db.database_service import DatabaseService
from src.riot_scraper.riot_api.riot_api_client import RiotApiClient
from src.riot_scraper.job_runner import JobRunner

logger = logging.getLogger('scraper')


class RiotTournamentScraper:
    def __init__(
            self,
            database_service: DatabaseService,
            riot_api_requester: RiotApiClient,
            job_runner: JobRunner
    ):
        self.db = database_service
        self.riot_api_requester = riot_api_requester
        self.job_runner = job_runner

    def fetch_tournaments_retry_job(self) -> None:
        self.job_runner.run_retry_job(
            job_function=self.fetch_tournaments_job,
            job_name="fetch tournaments job",
            max_retries=3
        )

    def fetch_tournaments_job(self) -> None:
        stored_leagues = self.db.get_leagues()
        for league in stored_leagues:
            get_tournaments_response = self.riot_api_requester.get_tournament_for_league(league.id)
            for tournament_league in get_tournaments_response.data.leagues:
                for tournament in tournament_league.tournaments:
                    new_tournament = Tournament(
                        id=tournament.id,
                        slug=tournament.slug,
                        start_date=tournament.startDate,
                        end_date=tournament.endDate,
                        league_id=league.id
                    )
                    self.db.put_tournament(new_tournament)
