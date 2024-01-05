import logging
from typing import List
from fantasylol.db import crud
from fantasylol.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from fantasylol.db.models import ProfessionalPlayer
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.schemas.search_parameters import PlayerSearchParameters


class RiotProfessionalPlayerService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_professional_players(self) -> List[ProfessionalPlayer]:
        logging.info("Fetching and storing professional players from riot's api")
        request_url = "https://esports-api.lolesports.com/persisted/gw/getTeams?hl=en-GB"
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            fetched_players = []
            for team in res_json['data']['teams']:
                for player in team['players']:
                    player_attrs = {
                        "id": int(player['id']),
                        "summoner_name": player['summonerName'],
                        "image": player['image'],
                        "role": player['role'],
                        "team_id": int(team['id'])
                    }
                    new_professional_player = ProfessionalPlayer(**player_attrs)
                    fetched_players.append(new_professional_player)
            for new_professional_player in fetched_players:
                crud.save_player(new_professional_player)
            return fetched_players
        except Exception as e:
            logging.error(f"{str(e)}")
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
