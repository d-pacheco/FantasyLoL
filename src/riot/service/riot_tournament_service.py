import logging
from datetime import datetime
from typing import List

from src.common.schemas.riot_data_schemas import Tournament, TournamentStatus, RiotTournamentID
from src.common.schemas.search_parameters import TournamentSearchParameters

from src.db.database_service import DatabaseService
from src.db.models import TournamentModel

from src.riot.exceptions import TournamentNotFoundException
from src.riot.util import RiotApiRequester
from src.riot.job_runner import JobRunner

logger = logging.getLogger('riot')


class RiotTournamentService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        self.riot_api_requester = RiotApiRequester()
        self.job_runner = JobRunner()

    def fetch_tournaments_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.fetch_tournaments_job,
            job_name="fetch tournaments job",
            max_retries=3
        )

    def fetch_tournaments_job(self):
        stored_leagues = self.db.get_leagues()

        fetched_tournaments = []
        for league in stored_leagues:
            tournaments = self.riot_api_requester.get_tournament_for_league(league.id)
            for tournament in tournaments:
                self.db.put_tournament(tournament)
                fetched_tournaments.append(tournament)

    def get_tournaments(self, search_parameters: TournamentSearchParameters) -> List[Tournament]:
        filters = []
        current_date = datetime.now()
        if search_parameters.status == TournamentStatus.ACTIVE:
            filters.append(TournamentModel.start_date <= current_date)
            filters.append(TournamentModel.end_date >= current_date)
        if search_parameters.status == TournamentStatus.COMPLETED:
            filters.append(TournamentModel.end_date < current_date)
        if search_parameters.status == TournamentStatus.UPCOMING:
            filters.append(TournamentModel.start_date > current_date)

        tournaments = self.db.get_tournaments(filters)
        return tournaments

    def get_tournament_by_id(self, tournament_id: RiotTournamentID) -> Tournament:
        tournament_orm = self.db.get_tournament_by_id(tournament_id)
        if tournament_orm is None:
            raise TournamentNotFoundException()
        tournament = Tournament.model_validate(tournament_orm)
        return tournament
