from db.database import DatabaseConnection
from util.RiotApiRequester import RiotApiRequester
from db.models import League

class RiotLeagueService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_leagues(self):
        print("Fetching and storing leagues from riot's api")
        request_url = "https://esports-api.lolesports.com/persisted/gw/getLeagues?hl=en-GB"
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            returned_leagues = []

            for league in res_json['data']['leagues']:
                new_league = League()
                new_league.id = int(league['id'])
                new_league.slug = league['slug']
                new_league.name = league['name']
                new_league.region = league['region']
                new_league.image = league['image']
                new_league.priority = league['priority']
                returned_leagues.append(new_league)
            
            for new_league in returned_leagues:
                with DatabaseConnection() as db:
                    db.merge(new_league)
                    db.commit()
        except Exception as e:
            random = 3
