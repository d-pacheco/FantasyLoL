import logging
from datetime import datetime
from typing import List

from src.common.schemas.riot_data_schemas import Tournament, TournamentStatus, RiotTournamentID
from src.common.schemas.search_parameters import TournamentSearchParameters

from src.db import crud
from src.db.models import TournamentModel

from src.riot.exceptions import TournamentNotFoundException
from src.riot.util import RiotApiRequester
from src.riot.job_runner import JobRunner

logger = logging.getLogger('fantasy-lol')


class RiotTournamentService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()
        self.job_runner = JobRunner()

    def fetch_tournaments_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.fetch_tournaments_job,
            job_name="fetch tournaments job",
            max_retries=3
        )

    def fetch_tournaments_job(self):
        stored_leagues = crud.get_leagues()

        fetched_tournaments = []
        for league in stored_leagues:
            tournaments = self.riot_api_requester.get_tournament_for_league(league.id)
            for tournament in tournaments:
                crud.put_tournament(tournament)
                fetched_tournaments.append(tournament)

    @staticmethod
    def get_tournaments(search_parameters: TournamentSearchParameters) -> List[Tournament]:
        filters = []
        current_date = datetime.now()
        if search_parameters.status == TournamentStatus.ACTIVE:
            filters.append(TournamentModel.start_date <= current_date)
            filters.append(TournamentModel.end_date >= current_date)
        if search_parameters.status == TournamentStatus.COMPLETED:
            filters.append(TournamentModel.end_date < current_date)
        if search_parameters.status == TournamentStatus.UPCOMING:
            filters.append(TournamentModel.start_date > current_date)

        tournaments = crud.get_tournaments(filters)
        return tournaments

    @staticmethod
    def get_tournament_by_id(tournament_id: RiotTournamentID) -> Tournament:
        tournament_orm = crud.get_tournament_by_id(tournament_id)
        if tournament_orm is None:
            raise TournamentNotFoundException()
        tournament = Tournament.model_validate(tournament_orm)
        return tournament
