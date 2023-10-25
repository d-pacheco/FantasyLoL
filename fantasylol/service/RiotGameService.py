from db.database import DatabaseConnection
from util.RiotApiRequester import RiotApiRequester
from db.models import Game

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
                    new_game = Game()
                    new_game.id = game['id']
                    new_game.start_time = event['startTime']
                    new_game.block_name = event['blockName']
                    new_game.strategy_type = event['match']['strategy']['type']
                    new_game.strategy_count = event['match']['strategy']['count']
                    new_game.state = game['state']
                    new_game.number = game['number']
                    new_game.tournament_id = tournament_id
                    new_game.team_1_id = game['teams'][0]['id']
                    new_game.team_2_id = game['teams'][1]['id']
                    returned_games.append(new_game)
                    
            for new_game in returned_games:
                with DatabaseConnection() as db:
                    db.merge(new_game)
                    db.commit()
        except Exception as e:
            random = 3