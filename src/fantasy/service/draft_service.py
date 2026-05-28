import logging
import math

from src.db.database_service import DatabaseService
from src.common.schemas.fantasy_schemas import (
    DraftPick,
    DraftState,
    FantasyLeagueID,
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    FantasyTeam,
    UserID,
    UserSlots,
)
from src.common.schemas.riot_data_schemas import ProPlayerID, ProTeamID, PlayerRole
from src.fantasy.exceptions import (
    FantasyDraftException,
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

    def make_pick(
        self,
        league_id: FantasyLeagueID,
        user_id: UserID,
        player_id: ProPlayerID | None = None,
        team_id: ProTeamID | None = None,
    ) -> DraftPick:
        # Validate league is in DRAFT status
        fantasy_league = self.fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.DRAFT]
        )

        # Validate exactly one of player_id or team_id
        if player_id is None and team_id is None:
            raise FantasyDraftException("Must provide either player_id or team_id")
        if player_id is not None and team_id is not None:
            raise FantasyDraftException("Cannot provide both player_id and team_id")

        # Determine whose turn it is via snake order
        existing_picks = self.db.get_draft_picks_for_league(league_id)
        pick_number = len(existing_picks) + 1
        num_users = fantasy_league.number_of_teams
        round_number = math.ceil(pick_number / num_users)
        position_in_round = pick_number - (round_number - 1) * num_users

        # Snake: odd rounds go 1→N, even rounds go N→1
        if round_number % 2 == 0:
            draft_position = num_users - position_in_round + 1
        else:
            draft_position = position_in_round

        # Map draft_position to user via draft order
        draft_order = self.db.get_fantasy_league_draft_order(league_id)
        expected_user_id = None
        for entry in draft_order:
            if entry.position == draft_position:
                expected_user_id = entry.user_id
                break

        if user_id != expected_user_id:
            raise FantasyDraftException(
                f"Not your turn: Expected user at position {draft_position}, got {user_id}"
            )

        # Get or create user's fantasy team for week 0 (draft week)
        user_teams = self.db.get_all_fantasy_teams_for_user(league_id, user_id)
        if user_teams:
            fantasy_team = user_teams[-1]
        else:
            fantasy_team = FantasyTeam(fantasy_league_id=league_id, user_id=user_id, week=0)

        if player_id is not None:
            # Validate player
            player = self.db.get_player_by_id(player_id)
            if player is None:
                raise FantasyDraftException(f"Player not found: {player_id}")
            if player.role == PlayerRole.NONE:
                raise FantasyDraftException(
                    f"Player has role=none and cannot be drafted: {player_id}"
                )

            # Validate player from available leagues
            player_league_ids = self.db.get_league_ids_for_player(player_id)
            if not any(lid in fantasy_league.available_leagues for lid in player_league_ids):
                raise FantasyDraftException(f"Player not from available leagues: {player_id}")

            # Validate player not already drafted
            for pick in existing_picks:
                if pick.player_id == player_id:
                    raise FantasyDraftException(f"Player already drafted: {player_id}")

            # Validate role slot empty
            if fantasy_team.get_player_id_for_role(player.role) is not None:
                raise FantasyDraftException(f"Role slot already filled: {player.role.value}")

            # Update fantasy team
            fantasy_team.set_player_id_for_role(player_id, player.role)

        else:
            # team_id pick
            team = self.db.get_team_by_id(team_id)
            if team is None:
                raise FantasyDraftException(f"Team not found: {team_id}")

            # Validate team not already drafted
            for pick in existing_picks:
                if pick.team_id == team_id:
                    raise FantasyDraftException(f"Team already drafted: {team_id}")

            # Validate team slot empty
            if fantasy_team.team_id is not None:
                raise FantasyDraftException("Team slot already filled")

            # Update fantasy team
            fantasy_team.team_id = team_id

        # Persist
        draft_pick = DraftPick(
            fantasy_league_id=league_id,
            pick_number=pick_number,
            round_number=round_number,
            user_id=user_id,
            player_id=player_id,
            team_id=team_id,
        )
        self.db.put_draft_pick(draft_pick)
        self.db.put_fantasy_team(fantasy_team)

        # Advance draft position or complete draft
        total_picks = 6 * num_users
        if pick_number >= total_picks:
            # Draft complete
            self.db.update_fantasy_league_status(league_id, FantasyLeagueStatus.ACTIVE)
            self.db.update_fantasy_league_current_week(league_id, 1)
        else:
            next_pick = pick_number + 1
            next_round = math.ceil(next_pick / num_users)
            next_pos_in_round = next_pick - (next_round - 1) * num_users
            if next_round % 2 == 0:
                next_draft_position = num_users - next_pos_in_round + 1
            else:
                next_draft_position = next_pos_in_round
            self.db.update_fantasy_league_current_draft_position(league_id, next_draft_position)

        return draft_pick

    def get_draft_state(self, league_id: FantasyLeagueID, user_id: UserID) -> DraftState:
        fantasy_league = self.fantasy_league_util.validate_league(
            league_id,
            [FantasyLeagueStatus.DRAFT, FantasyLeagueStatus.ACTIVE, FantasyLeagueStatus.COMPLETED],
        )
        self.fantasy_league_util.validate_membership(user_id, league_id)

        num_users = fantasy_league.number_of_teams
        total_picks = 6 * num_users
        existing_picks = self.db.get_draft_picks_for_league(league_id)
        current_pick_number = len(existing_picks) + 1
        is_complete = len(existing_picks) >= total_picks

        # Determine current round and whose turn
        if is_complete:
            current_round = 6
            current_turn_user_id = None
        else:
            current_round = math.ceil(current_pick_number / num_users)
            pos_in_round = current_pick_number - (current_round - 1) * num_users
            if current_round % 2 == 0:
                draft_position = num_users - pos_in_round + 1
            else:
                draft_position = pos_in_round

            draft_order = self.db.get_fantasy_league_draft_order(league_id)
            current_turn_user_id = None
            for entry in draft_order:
                if entry.position == draft_position:
                    current_turn_user_id = entry.user_id
                    break

        # Build user slots from fantasy teams
        user_slots: dict[str, UserSlots] = {}
        draft_order = self.db.get_fantasy_league_draft_order(league_id)
        for entry in draft_order:
            teams = self.db.get_all_fantasy_teams_for_user(league_id, entry.user_id)
            if teams:
                t = teams[-1]
                user_slots[entry.user_id] = UserSlots(
                    top_player_id=t.top_player_id,
                    jungle_player_id=t.jungle_player_id,
                    mid_player_id=t.mid_player_id,
                    adc_player_id=t.adc_player_id,
                    support_player_id=t.support_player_id,
                    team_id=t.team_id,
                )
            else:
                user_slots[entry.user_id] = UserSlots()

        return DraftState(
            fantasy_league_id=league_id,
            current_round=current_round,
            current_pick_number=current_pick_number,
            total_picks=total_picks,
            current_turn_user_id=current_turn_user_id,
            picks=existing_picks,
            user_slots=user_slots,
            is_complete=is_complete,
        )
