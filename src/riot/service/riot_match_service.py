import logging
from datetime import datetime, timezone, timedelta

from src.common.schemas.riot_data_schemas import Match, RiotMatchID, MatchState
from src.common.schemas.search_parameters import MatchSearchParameters
from src.db.database_service import DatabaseService
from src.db.views import MatchView
from src.riot.exceptions import MatchNotFoundException

logger = logging.getLogger("api.riot")


class RiotMatchService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_matches(self, search_parameters: MatchSearchParameters) -> list[Match]:
        filters = []
        if search_parameters.league_slug is not None:
            filters.append(MatchView.league_slug == search_parameters.league_slug)
        if search_parameters.tournament_id is not None:
            filters.append(MatchView.tournament_id == search_parameters.tournament_id)
        matches = self.db.get_matches(filters)
        return matches

    def get_match_by_id(self, match_id: RiotMatchID) -> Match:
        match = self.db.get_match_by_id(match_id)
        if match is None:
            raise MatchNotFoundException()
        return match

    def get_schedule(self) -> dict[str, list[Match]]:
        all_matches = self.db.get_fantasy_schedule_matches()
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=48)
        cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

        live = []
        upcoming = []
        recent = []

        for match in all_matches:
            if match.state == MatchState.INPROGRESS:
                live.append(match)
            elif match.state == MatchState.UNSTARTED:
                upcoming.append(match)
            elif match.state == MatchState.COMPLETED and match.start_time >= cutoff_str:
                recent.append(match)

        upcoming.sort(key=lambda m: m.start_time)
        recent.sort(key=lambda m: m.start_time, reverse=True)

        return {"live": live, "upcoming": upcoming, "recent": recent}
