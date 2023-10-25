from db.database import DatabaseConnection
from db.models import League
from exceptions.RiotApiStatusException import RiotApiStatusCodeAssertException
from util.RiotApiRequester import RiotApiRequester

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
                league_attrs = {
                    "id": int(league['id']),
                    "slug": league['slug'],
                    "name": league['name'],
                    "region": league['region'],
                    "image": league['image'],
                    "priority": league['priority']
                }
                new_league = League(**league_attrs)
                returned_leagues.append(new_league)
            
            for new_league in returned_leagues:
                with DatabaseConnection() as db:
                    db.merge(new_league)
                    db.commit()
        except RiotApiStatusCodeAssertException as e:
            print(f"Error: {str(e)}")
            raise e
        except Exception as e:
            print(f"Error: {str(e)}")
