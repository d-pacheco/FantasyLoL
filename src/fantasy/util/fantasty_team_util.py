from src.common.schemas.fantasy_schemas import FantasyLeague, UserID
from src.common.schemas.riot_data_schemas import ProPlayerID

from src.db.database_service import DatabaseService

from src.fantasy.exceptions import FantasyDraftException


class FantasyTeamUtil:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        
    def validate_player_from_available_league(
            self,
            fantasy_league: FantasyLeague,
            player_id: ProPlayerID
    ) -> None:
        player_league_ids = self.db.get_league_ids_for_player(player_id)
        in_allowed_league = False
        for available_league_id in fantasy_league.available_leagues:
            if available_league_id in player_league_ids:
                in_allowed_league = True
                break
        if not in_allowed_league:
            raise FantasyDraftException(
                f"Player not in available league: Player with ID {player_id} is not from "
                f"one of the available leagues {fantasy_league.available_leagues}, for the "
                f"fantasy league with ID {fantasy_league.id}"
            )

    def is_users_position_to_draft(self, fantasy_league: FantasyLeague, user_id: UserID) -> bool:
        draft_order = self.db.get_fantasy_league_draft_order(fantasy_league.id)
        users_draft_position = None
        for draft_position in draft_order:
            if draft_position.user_id == user_id:
                users_draft_position = draft_position.position
        if users_draft_position is None:
            # This should ideally never be hit since we are validating the users
            # membership before we call this method.
            raise FantasyDraftException(
                f"Could not find draft position for user with ID {user_id} "
                f"in the fantasy league with ID {fantasy_league.id}"
            )

        return users_draft_position == fantasy_league.current_draft_position

    def all_teams_fully_drafted(self, fantasy_league: FantasyLeague) -> bool:
        assert (fantasy_league.current_week is not None)
        fantasy_league_teams = self.db.get_all_fantasy_teams_for_week(
            fantasy_league.id, fantasy_league.current_week
        )
        if len(fantasy_league_teams) != fantasy_league.number_of_teams:
            return False

        all_teams_fully_draft = True
        for team in fantasy_league_teams:
            if team.top_player_id is None:
                all_teams_fully_draft = False
                break
            if team.jungle_player_id is None:
                all_teams_fully_draft = False
                break
            if team.mid_player_id is None:
                all_teams_fully_draft = False
                break
            if team.adc_player_id is None:
                all_teams_fully_draft = False
                break
            if team.support_player_id is None:
                all_teams_fully_draft = False
                break
        return all_teams_fully_draft
