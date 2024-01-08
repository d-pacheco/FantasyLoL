import logging
from typing import List
from fantasylol.db import crud
from fantasylol.db.models import League
from fantasylol.exceptions.league_not_found_exception import LeagueNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.schemas.search_parameters import LeagueSearchParameters

logger = logging.getLogger('fantasy-lol')


class RiotLeagueService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_leagues(self) -> List[League]:
        logger.info("Fetching and storing leagues from riot's api")
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
                crud.save_league(new_league)
            return fetched_leagues
        except Exception as e:
            logger.error(f"{str(e)}")
            raise e

    @staticmethod
    def get_leagues(search_parameters: LeagueSearchParameters) -> List[League]:
        filters = []
        if search_parameters.name is not None:
            filters.append(League.name == search_parameters.name)
        if search_parameters.region is not None:
            filters.append(League.region == search_parameters.region)
        leagues = crud.get_leagues(filters)
        return leagues

    @staticmethod
    def get_league_by_id(league_id: int) -> League:
        league = crud.get_league_by_id(league_id)
        if league is None:
            raise LeagueNotFoundException()
        return league
