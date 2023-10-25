from db.database import DatabaseConnection
from db.models import Game
from util.RiotApiRequester import RiotApiRequester
from exceptions.RiotApiStatusException import RiotApiStatusCodeAssertException

class RiotGameService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_live_games(self):
        print("Fetching and storing live games from riot's api")
        request_url = "https://esports-api.lolesports.com/persisted/gw/getLive?hl=en-GB"
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            returned_games = []
            events = res_json["data"]["schedule"].get("events", [])
            for event in events:
                if event['type'] != 'match':
                    continue
                tournament_id = event['tournament']['id']
                games = event['match']['games']
                for game in games:
                    if game['state'] != 'inProgress':
                        continue
                    new_game_attrs = {
                        "id": game['id'],
                        "start_time": event['startTime'],
                        "block_name": event['blockName'],
                        "strategy_type": event['match']['strategy']['type'],
                        "strategy_count": event['match']['strategy']['count'],
                        "state": game['state'],
                        "number": game['number'],
                        "tournament_id": tournament_id,
                        "team_1_id": game['teams'][0]['id'],
                        "team_2_id": game['teams'][1]['id'],
                    }
                    new_game = Game(**new_game_attrs)
                    returned_games.append(new_game)
                    
            for new_game in returned_games:
                with DatabaseConnection() as db:
                    db.merge(new_game)
                    db.commit()
        except RiotApiStatusCodeAssertException as e:
            print(f"Error: {str(e)}")
            raise e
        except Exception as e:
            print(f"Error: {str(e)}")