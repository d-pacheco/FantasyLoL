from db.database import DatabaseConnection
from util.RiotApiRequester import RiotApiRequester
from db.models import League
from db.models import Tournament

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
                    new_tournament = Tournament()
                    new_tournament.id = int(tournament['id'])
                    new_tournament.slug = tournament['slug']
                    new_tournament.start_date = tournament['startDate']
                    new_tournament.end_date = tournament['endDate']
                    new_tournament.league_id = league_id
                    returned_tournaments.append(new_tournament)
            
            for new_tournament in returned_tournaments:
                with DatabaseConnection() as db:
                    db.merge(new_tournament)
                    db.commit()
        except Exception as e:
            random = 3
