import logging
from typing import List
from fantasylol.db import crud
from fantasylol.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from fantasylol.db.models import ProfessionalPlayer
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.schemas.search_parameters import PlayerSearchParameters
from fantasylol.schemas.riot_data_schemas import ProfessionalPlayerSchema

logger = logging.getLogger('fantasy-lol')


class RiotProfessionalPlayerService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_professional_players(self) -> List[ProfessionalPlayerSchema]:
        logger.info("Fetching and storing professional players from riot's api")
        try:
            fetched_players = self.riot_api_requester.get_players()
            for player in fetched_players:
                crud.save_player(player)
            return fetched_players
        except Exception as e:
            logger.error(f"{str(e)}")
            raise e

    @staticmethod
    def get_players(search_parameters: PlayerSearchParameters) -> List[ProfessionalPlayer]:
        filters = []
        if search_parameters.summoner_name is not None:
            filters.append(ProfessionalPlayer.summoner_name == search_parameters.summoner_name)
        if search_parameters.team_id is not None:
            filters.append(ProfessionalPlayer.team_id == search_parameters.team_id)
        if search_parameters.role is not None:
            filters.append(ProfessionalPlayer.role == search_parameters.role)

        professional_players = crud.get_players(filters)
        return professional_players

    @staticmethod
    def get_player_by_id(professional_player_id: int) -> ProfessionalPlayer:
        professional_player = crud.get_player_by_id(professional_player_id)
        if professional_player is None:
            raise ProfessionalPlayerNotFoundException()
        return professional_player
