import logging
from datetime import datetime

from src.common.schemas.riot_data_schemas import Tournament, TournamentStatus, RiotTournamentID
from src.common.schemas.search_parameters import TournamentSearchParameters
from src.db.database_service import DatabaseService
from src.db.models import TournamentModel
from src.riot.exceptions import TournamentNotFoundException

logger = logging.getLogger("riot")


class RiotTournamentService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_tournaments(self, search_parameters: TournamentSearchParameters) -> list[Tournament]:
        filters = []
        current_date = datetime.now().strftime("%Y-%m-%d")
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
