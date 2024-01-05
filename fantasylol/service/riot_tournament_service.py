import logging
from datetime import datetime
from typing import List

from fantasylol.db import crud
from fantasylol.db.models import Tournament
from fantasylol.exceptions.tournament_not_found_exception import TournamentNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.schemas.tournament_status import TournamentStatus
from fantasylol.schemas.search_parameters import TournamentSearchParameters


class RiotTournamentService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_tournaments(self) -> List[Tournament]:
        logging.info("Fetching and storing tournaments from riot's api")
        request_url = "https://esports-api.lolesports.com/persisted/gw" \
                      "/getTournamentsForLeague?hl=en-GB&leagueId={id}"
        try:
            league_ids = []
            stored_leagues = crud.get_leagues()
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
                crud.save_tournament(new_tournament)
            return fetched_tournaments
        except Exception as e:
            logging.error(f"{str(e)}")
            raise e

    @staticmethod
    def get_tournaments(search_parameters: TournamentSearchParameters) -> List[Tournament]:
        filters = []
        current_date = datetime.now()
        if search_parameters.status == TournamentStatus.ACTIVE:
            filters.append(Tournament.start_date <= current_date)
            filters.append(Tournament.end_date >= current_date)
        if search_parameters.status == TournamentStatus.COMPLETED:
            filters.append(Tournament.end_date < current_date)
        if search_parameters.status == TournamentStatus.UPCOMING:
            filters.append(Tournament.start_date > current_date)

        tournaments = crud.get_tournaments(filters)
        return tournaments

    @staticmethod
    def get_tournament_by_id(tournament_id: int) -> Tournament:
        tournament = crud.get_tournament_by_id(tournament_id)
        if tournament is None:
            raise TournamentNotFoundException()
        return tournament
