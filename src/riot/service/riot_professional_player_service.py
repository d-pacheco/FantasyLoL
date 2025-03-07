import logging
from typing import List

from src.common.schemas.search_parameters import PlayerSearchParameters
from src.common.schemas.riot_data_schemas import ProfessionalPlayer, ProPlayerID

from src.db.database_service import DatabaseService
from src.db.models import ProfessionalPlayerModel

from src.common.exceptions import ProfessionalPlayerNotFoundException
from src.riot.util import RiotApiRequester
from src.riot.job_runner import JobRunner

logger = logging.getLogger('riot')


class RiotProfessionalPlayerService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        self.riot_api_requester = RiotApiRequester()
        self.job_runner = JobRunner()

    def fetch_professional_players_from_riot_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.fetch_professional_players_from_riot_job,
            job_name="fetch players from riot job",
            max_retries=3
        )

    def fetch_professional_players_from_riot_job(self):
        fetched_players = self.riot_api_requester.get_players()
        for player in fetched_players:
            self.db.put_player(player)

    def get_players(self, search_parameters: PlayerSearchParameters) -> List[ProfessionalPlayer]:
        filters = []
        if search_parameters.summoner_name is not None:
            filters.append(ProfessionalPlayerModel.summoner_name == search_parameters.summoner_name)
        if search_parameters.team_id is not None:
            filters.append(ProfessionalPlayerModel.team_id == search_parameters.team_id)
        if search_parameters.role is not None:
            filters.append(ProfessionalPlayerModel.role == search_parameters.role)

        professional_players = self.db.get_players(filters)
        return professional_players

    def get_player_by_id(self, professional_player_id: ProPlayerID) -> ProfessionalPlayer:
        professional_player = self.db.get_player_by_id(professional_player_id)
        if professional_player is None:
            raise ProfessionalPlayerNotFoundException()
        return professional_player
