import logging
from datetime import datetime
from typing import List

from fantasylol.db import crud
from fantasylol.db.models import Tournament
from fantasylol.schemas.riot_data_schemas import TournamentSchema
from fantasylol.exceptions.tournament_not_found_exception import TournamentNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.schemas.tournament_status import TournamentStatus
from fantasylol.schemas.search_parameters import TournamentSearchParameters

logger = logging.getLogger('fantasy-lol')


class RiotTournamentService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_tournaments(self) -> List[TournamentSchema]:
        logger.info("Fetching and storing tournaments from riot's api")
        try:
            stored_leagues = crud.get_leagues()

            fetched_tournaments = []
            for league in stored_leagues:
                tournaments = self.riot_api_requester.get_tournament_for_league(league.id)
                for tournament in tournaments:
                    crud.save_tournament(tournament)
                    fetched_tournaments.append(tournament)
            return fetched_tournaments
        except Exception as e:
            logger.error(f"{str(e)}")
            raise e

    @staticmethod
    def get_tournaments(search_parameters: TournamentSearchParameters) -> List[TournamentSchema]:
        filters = []
        current_date = datetime.now()
        if search_parameters.status == TournamentStatus.ACTIVE:
            filters.append(Tournament.start_date <= current_date)
            filters.append(Tournament.end_date >= current_date)
        if search_parameters.status == TournamentStatus.COMPLETED:
            filters.append(Tournament.end_date < current_date)
        if search_parameters.status == TournamentStatus.UPCOMING:
            filters.append(Tournament.start_date > current_date)

        tournament_orms = crud.get_tournaments(filters)
        tournaments = [TournamentSchema.model_validate(tournament_orm)
                       for tournament_orm in tournament_orms]
        return tournaments

    @staticmethod
    def get_tournament_by_id(tournament_id: str) -> TournamentSchema:
        tournament_orm = crud.get_tournament_by_id(tournament_id)
        if tournament_orm is None:
            raise TournamentNotFoundException()
        tournament = TournamentSchema.model_validate(tournament_orm)
        return tournament
