from typing import List, Optional

from src.common.exceptions import LeagueNotFoundException
from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueDraftOrder,
    FantasyLeagueDraftOrderResponse,
    FantasyLeagueID,
    FantasyLeagueStatus,
    UserID
)
from src.common.schemas.riot_data_schemas import RiotLeagueID

from src.db.database_service import DatabaseService

from src.fantasy.exceptions import (
    FantasyLeagueNotFoundException,
    FantasyLeagueInvalidRequiredStateException,
    FantasyUnavailableException,
    DraftOrderException
)


class FantasyLeagueUtil:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def validate_league(
            self,
            fantasy_league_id: FantasyLeagueID,
            required_states: Optional[List[FantasyLeagueStatus]] = None) -> FantasyLeague:
        fantasy_league = self.db.get_fantasy_league_by_id(fantasy_league_id)
        if fantasy_league is None:
            raise FantasyLeagueNotFoundException()
        if (required_states is not None) and (fantasy_league.status not in required_states):
            raise FantasyLeagueInvalidRequiredStateException(
                fantasy_league_id, fantasy_league.status, required_states
            )

        return fantasy_league

    def validate_available_leagues(self, selected_league_ids: List[RiotLeagueID]) -> None:
        riot_leagues = self.db.get_leagues()
        league_dict = {league.id: league for league in riot_leagues}

        for league_id in selected_league_ids:
            if league_id not in league_dict:
                raise LeagueNotFoundException(league_id)
            if not league_dict[league_id].fantasy_available:
                raise FantasyUnavailableException(league_id)

    def update_fantasy_leagues_current_draft_position(self, fantasy_league: FantasyLeague) -> None:
        assert (fantasy_league.current_draft_position is not None)
        if fantasy_league.current_draft_position + 1 <= fantasy_league.number_of_teams:
            new_draft_position = fantasy_league.current_draft_position + 1
        else:
            new_draft_position = 1
        self.db.update_fantasy_league_current_draft_position(fantasy_league.id, new_draft_position)

    def create_draft_order_entry(self, user_id: UserID, league_id: FantasyLeagueID) -> None:
        fantasy_league = self.db.get_fantasy_league_by_id(league_id)
        if fantasy_league is None:
            raise FantasyLeagueNotFoundException()

        current_draft_order = self.db.get_fantasy_league_draft_order(league_id)
        if len(current_draft_order) == 0:
            max_position = 0
        else:
            max_position = max(
                current_draft_order, key=lambda draft_position: draft_position.position
            ).position

        new_draft_position = FantasyLeagueDraftOrder(
            fantasy_league_id=league_id,
            user_id=user_id,
            position=max_position + 1
        )
        self.db.create_fantasy_league_draft_order(new_draft_position)

    @staticmethod
    def validate_draft_order(
            current_draft_order: List[FantasyLeagueDraftOrder],
            updated_draft_order: List[FantasyLeagueDraftOrderResponse]
    ) -> None:
        member_ids = [draft_position.user_id for draft_position in current_draft_order]

        if len(updated_draft_order) != len(current_draft_order):
            raise DraftOrderException(
                "Draft order contains more or less players than current draft"
            )

        for draft_order in updated_draft_order:
            if draft_order.user_id not in member_ids:
                raise DraftOrderException(f"User {draft_order.user_id} is not in current draft")

        positions = [draft_position.position for draft_position in updated_draft_order]
        positions.sort()
        expected_positions = list(range(1, len(current_draft_order) + 1))
        if positions != expected_positions:
            raise DraftOrderException(
                "The positions given in the updated draft order are not valid"
            )

    def update_draft_order_on_player_leave(
            self,
            user_id: UserID,
            league_id: FantasyLeagueID
    ) -> None:
        current_draft_order = self.db.get_fantasy_league_draft_order(league_id)

        draft_position_to_delete: Optional[FantasyLeagueDraftOrder] = None
        for draft_position in current_draft_order:
            if draft_position.user_id == user_id:
                draft_position_to_delete = draft_position
                break
        if draft_position_to_delete is None:
            raise DraftOrderException(
                f"Missing user on draft removal: User with ID {user_id} does not have a draft "
                f"position in fantasy league with ID {league_id}"
            )

        self.db.delete_fantasy_league_draft_order(draft_position_to_delete)
        for draft_position in current_draft_order:
            if draft_position.position > draft_position_to_delete.position:
                self.db.update_fantasy_league_draft_order_position(
                    draft_position, draft_position.position - 1
                )
