import logging
from typing import List
from fantasylol.db import crud
from fantasylol.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from fantasylol.db.models import ProfessionalPlayerModel
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.schemas.search_parameters import PlayerSearchParameters
from fantasylol.schemas.riot_data_schemas import ProfessionalPlayer

logger = logging.getLogger('fantasy-lol')


class RiotProfessionalPlayerService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_professional_players(self) -> List[ProfessionalPlayer]:
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
            filters.append(ProfessionalPlayerModel.summoner_name == search_parameters.summoner_name)
        if search_parameters.team_id is not None:
            filters.append(ProfessionalPlayerModel.team_id == search_parameters.team_id)
        if search_parameters.role is not None:
            filters.append(ProfessionalPlayerModel.role == search_parameters.role)

        professional_players_orms = crud.get_players(filters)
        professional_players = [ProfessionalPlayer.model_validate(player_orm)
                                for player_orm in professional_players_orms]
        return professional_players

    @staticmethod
    def get_player_by_id(professional_player_id: str) -> ProfessionalPlayer:
        professional_player_orm = crud.get_player_by_id(professional_player_id)
        if professional_player_orm is None:
            raise ProfessionalPlayerNotFoundException()
        professional_player = ProfessionalPlayer.model_validate(professional_player_orm)
        return professional_player
