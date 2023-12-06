from datetime import datetime
from typing import List

from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import League
from fantasylol.db.models import Tournament
from fantasylol.exceptions.tournament_not_found_exception import TournamentNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.schemas.tournament_status import TournamentStatus


class RiotTournamentService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_tournaments(self) -> List[Tournament]:
        print("Fetching and storing tournaments from riot's api")
        request_url = "https://esports-api.lolesports.com/persisted/gw" \
                      "/getTournamentsForLeague?hl=en-GB&leagueId={id}"
        try:
            league_ids = []
            with DatabaseConnection() as db:
                stored_leagues = db.query(League).all()
                for league in stored_leagues:
                    league_ids.append(league.id)

            fetched_tournaments = []
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
                    fetched_tournaments.append(new_tournament)

            for new_tournament in fetched_tournaments:
                with DatabaseConnection() as db:
                    db.merge(new_tournament)
                    db.commit()
            return fetched_tournaments
        except Exception as e:
            print(f"Error: {str(e)}")
            raise e

    def get_tournaments(self, status: TournamentStatus = None) -> List[Tournament]:
        current_date = datetime.now()

        with DatabaseConnection() as db:
            query = db.query(Tournament)
            if status == TournamentStatus.ACTIVE:
                tournaments = query.filter(Tournament.start_date <=
                                           current_date, Tournament.end_date >= current_date).all()
            elif status == TournamentStatus.COMPLETED:
                tournaments = query.filter(Tournament.end_date < current_date).all()
            elif status == TournamentStatus.UPCOMING:
                tournaments = query.filter(Tournament.start_date > current_date).all()
            else:
                tournaments = query.all()
        return tournaments

    def get_tournament_by_id(sself, tournament_id: int) -> Tournament:
        with DatabaseConnection() as db:
            tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if tournament is None:
            raise TournamentNotFoundException()
        return tournament
