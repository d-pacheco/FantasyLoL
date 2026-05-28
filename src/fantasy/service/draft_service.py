import logging

from src.db.database_service import DatabaseService
from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    UserID,
)
from src.fantasy.exceptions import (
    FantasyLeagueStartDraftException,
    ForbiddenException,
)
from src.fantasy.util import FantasyLeagueUtil

logger = logging.getLogger("api.fantasy")


class DraftService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        self.fantasy_league_util = FantasyLeagueUtil(database_service)

    def start_draft(self, league_id: FantasyLeagueID, owner_id: UserID) -> None:
        logger.info("Starting draft for league=%s by user=%s", league_id, owner_id)
        fantasy_league = self.fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.PRE_DRAFT]
        )
        if fantasy_league.owner_id != owner_id:
            raise ForbiddenException()

        pending_and_accepted_memberships = self.db.get_pending_and_accepted_members_for_league(
            league_id
        )
        accepted_count = sum(
            1
            for m in pending_and_accepted_memberships
            if m.status == FantasyLeagueMembershipStatus.ACCEPTED
        )
        if accepted_count != fantasy_league.number_of_teams:
            raise FantasyLeagueStartDraftException(
                f"Invalid member count: The fantasy league with ID {league_id} does not "
                f"have correct number of members to start the draft. "
                f"Expected {fantasy_league.number_of_teams} but has {accepted_count}."
            )

        if len(fantasy_league.available_leagues) == 0:
            raise FantasyLeagueStartDraftException(
                f"Available leagues not set: The fantasy league with ID {league_id} must "
                f"have one Riot league set for players to draft from before starting the draft."
            )

        self.db.update_fantasy_league_status(league_id, FantasyLeagueStatus.DRAFT)
        self.db.update_fantasy_league_current_draft_position(league_id, 1)
        self.db.update_fantasy_league_current_week(league_id, 0)
