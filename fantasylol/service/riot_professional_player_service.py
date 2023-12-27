from typing import List
from fantasylol.db.database import DatabaseConnection
from fantasylol.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from fantasylol.db.models import ProfessionalPlayer
from fantasylol.util.riot_api_requester import RiotApiRequester


class RiotProfessionalPlayerService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_professional_players(self) -> List[ProfessionalPlayer]:
        print("Fetching and storing professional players from riot's api")
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
                with DatabaseConnection() as db:
                    db.merge(new_professional_player)
                    db.commit()
            return fetched_players
        except Exception as e:
            print(f"Error: {str(e)}")
            raise e

    def get_players(self, query_params: dict = None) -> List[ProfessionalPlayer]:
        with DatabaseConnection() as db:
            query = db.query(ProfessionalPlayer)

            if query_params is None:
                return query.all()

            for param_key in query_params:
                param = query_params[param_key]
                if param is None:
                    continue
                column = getattr(ProfessionalPlayer, param_key, None)
                if column is not None:
                    query = query.filter(column == param)
            professional_players = query.all()
        return professional_players

    def get_player_by_id(self, professional_player_id: str) -> ProfessionalPlayer:
        with DatabaseConnection() as db:
            professional_player = db.query(ProfessionalPlayer).filter(
                ProfessionalPlayer.id == professional_player_id).first()
        if professional_player is None:
            raise ProfessionalPlayerNotFoundException()
        return professional_player
