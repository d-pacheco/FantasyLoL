import logging
from typing import List

from ...common.schemas.search_parameters import PlayerSearchParameters
from ...common.schemas.riot_data_schemas import ProfessionalPlayer, ProPlayerID

from ...db import crud
from ...db.models import ProfessionalPlayerModel

from ..exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from ..util.riot_api_requester import RiotApiRequester
from ..util.job_runner import JobRunner

logger = logging.getLogger('fantasy-lol')


class RiotProfessionalPlayerService:
    def __init__(self):
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
            crud.put_player(player)

    @staticmethod
    def get_players(search_parameters: PlayerSearchParameters) -> List[ProfessionalPlayer]:
        filters = []
        if search_parameters.summoner_name is not None:
            filters.append(ProfessionalPlayerModel.summoner_name == search_parameters.summoner_name)
        if search_parameters.team_id is not None:
            filters.append(ProfessionalPlayerModel.team_id == search_parameters.team_id)
        if search_parameters.role is not None:
            filters.append(ProfessionalPlayerModel.role == search_parameters.role)

        professional_players = crud.get_players(filters)
        return professional_players

    @staticmethod
    def get_player_by_id(professional_player_id: ProPlayerID) -> ProfessionalPlayer:
        professional_player = crud.get_player_by_id(professional_player_id)
        if professional_player is None:
            raise ProfessionalPlayerNotFoundException()
        return professional_player
