import logging

from src.common.schemas.riot_data_schemas import Match, RiotMatchID
from src.common.schemas.search_parameters import MatchSearchParameters
from src.db.database_service import DatabaseService
from src.db.models import MatchModel
from src.riot.exceptions import MatchNotFoundException

logger = logging.getLogger('riot')


class RiotMatchService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_matches(self, search_parameters: MatchSearchParameters) -> list[Match]:
        filters = []
        if search_parameters.league_slug is not None:
            filters.append(MatchModel.league_slug == search_parameters.league_slug)
        if search_parameters.tournament_id is not None:
            filters.append(MatchModel.tournament_id == search_parameters.tournament_id)
        matches = self.db.get_matches(filters)
        return matches

    def get_match_by_id(self, match_id: RiotMatchID) -> Match:
        match = self.db.get_match_by_id(match_id)
        if match is None:
            raise MatchNotFoundException()
        return match
