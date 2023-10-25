from db.database import DatabaseConnection
from db.models import League
from db.models import Tournament
from exceptions.RiotApiStatusException import RiotApiStatusCodeAssertException
from util.RiotApiRequester import RiotApiRequester

class RiotTournamentService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_tournaments(self):
        print("Fetching and storing tournaments from riot's api")
        request_url = "https://esports-api.lolesports.com/persisted/gw/getTournamentsForLeague?hl=en-GB&leagueId={id}"
        try:
            league_ids = []
            with DatabaseConnection() as db:
                stored_leagues = db.query(League).all()
                for league in stored_leagues:
                    league_ids.append(league.id)

            returned_tournaments = []
            for league_id in league_ids:
                res_json = self.riot_api_requester.make_request(request_url.format(id=league_id))
                tournaments = res_json['data']['leagues'][0]['tournaments']
                for tournament in tournaments:
                    tournament_attrs = {
                        "id": int(tournament['id']),
                        "slug": tournament['slug'],
                        "start_date": tournament['startDate'],
                        "end_date": tournament['endDate'],
                        "league_id": league_id
                    }
                    new_tournament = Tournament(**tournament_attrs)
                    returned_tournaments.append(new_tournament)
            
            for new_tournament in returned_tournaments:
                with DatabaseConnection() as db:
                    db.merge(new_tournament)
                    db.commit()
        except RiotApiStatusCodeAssertException as e:
            print(f"Error: {str(e)}")
            raise e
        except Exception as e:
            print(f"Error: {str(e)}")
