import logging
from typing import List
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import League
from fantasylol.exceptions.league_not_found_exception import LeagueNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester


class RiotLeagueService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_leagues(self) -> List[League]:
        logging.info("Fetching and storing leagues from riot's api")
        request_url = "https://esports-api.lolesports.com/persisted/gw/getLeagues?hl=en-GB"
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            fetched_leagues = []

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
                fetched_leagues.append(new_league)

            for new_league in fetched_leagues:
                with DatabaseConnection() as db:
                    db.merge(new_league)
                    db.commit()
            return fetched_leagues
        except Exception as e:
            logging.error(f"{str(e)}")
            raise e

    def get_leagues(self, query_params: dict = None) -> List[League]:
        with DatabaseConnection() as db:
            query = db.query(League)

            if query_params is None:
                return query.all()

            for param_key in query_params:
                param = query_params[param_key]
                if param is None:
                    continue
                column = getattr(League, param_key, None)
                if column is not None:
                    query = query.filter(column == param)
            leagues = query.all()
        return leagues

    def get_league_by_id(self, league_id: int) -> League:
        with DatabaseConnection() as db:
            league = db.query(League).filter(League.id == league_id).first()
        if league is None:
            raise LeagueNotFoundException()
        return league
