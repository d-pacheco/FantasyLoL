import logging
import math
import random

from src.db.database_service import DatabaseService
from src.db.models import ProfessionalPlayerModel, LeagueModel
from src.common.schemas.fantasy_schemas import (
    DraftPick,
    DraftState,
    FantasyLeagueID,
    FantasyLeagueDraftOrder,
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    FantasyTeam,
    UserID,
    UserSlots,
)
from src.common.schemas.riot_data_schemas import (
    ProfessionalPlayer,
    ProfessionalTeam,
    ProPlayerID,
    ProTeamID,
    PlayerRole,
)
from src.fantasy.exceptions import (
    FantasyDraftException,
    FantasyLeagueStartDraftException,
    ForbiddenException,
)
from src.fantasy.util import FantasyLeagueUtil

logger = logging.getLogger("api.fantasy")

PICKS_PER_USER = 6


def _snake_position(pick_number: int, num_users: int) -> int:
    """Return the draft_position (1-based) for a given pick_number using snake order.
    Odd rounds go 1→N, even rounds go N→1.
    """
    round_number = math.ceil(pick_number / num_users)
    position_in_round = pick_number - (round_number - 1) * num_users
    if round_number % 2 == 0:
        return num_users - position_in_round + 1
    return position_in_round


def _get_round(pick_number: int, num_users: int) -> int:
    """Return the round number (1-based) for a given pick_number."""
    return math.ceil(pick_number / num_users)


def _get_user_for_position(
    draft_order: list[FantasyLeagueDraftOrder], position: int
) -> UserID | None:
    """Find the user_id at the given draft position."""
    for entry in draft_order:
        if entry.position == position:
            return entry.user_id
    return None


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
        num_users = fantasy_league.number_of_teams
        existing_picks = self.db.get_draft_picks_for_league(league_id)
        pick_number = len(existing_picks) + 1
        round_number = _get_round(pick_number, num_users)
        draft_position = _snake_position(pick_number, num_users)

        # Validate it's the user's turn
        draft_order = self.db.get_fantasy_league_draft_order(league_id)
        expected_user_id = _get_user_for_position(draft_order, draft_position)
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
            self._validate_and_apply_player_pick(
                player_id, fantasy_league, fantasy_team, existing_picks
            )
        else:
            self._validate_and_apply_team_pick(team_id, fantasy_team, existing_picks)

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
        total_picks = PICKS_PER_USER * num_users
        if pick_number >= total_picks:
            self.db.update_fantasy_league_status(league_id, FantasyLeagueStatus.ACTIVE)
            self.db.update_fantasy_league_current_week(league_id, 1)
        else:
            next_position = _snake_position(pick_number + 1, num_users)
            self.db.update_fantasy_league_current_draft_position(league_id, next_position)

        return draft_pick

    def get_draft_state(self, league_id: FantasyLeagueID, user_id: UserID) -> DraftState:
        fantasy_league = self.fantasy_league_util.validate_league(
            league_id,
            [FantasyLeagueStatus.DRAFT, FantasyLeagueStatus.ACTIVE, FantasyLeagueStatus.COMPLETED],
        )
        self.fantasy_league_util.validate_membership(user_id, league_id)

        num_users = fantasy_league.number_of_teams
        total_picks = PICKS_PER_USER * num_users
        existing_picks = self.db.get_draft_picks_for_league(league_id)
        current_pick_number = len(existing_picks) + 1
        is_complete = len(existing_picks) >= total_picks

        # Determine current round and whose turn
        if is_complete:
            current_round = PICKS_PER_USER
            current_turn_user_id = None
        else:
            current_round = _get_round(current_pick_number, num_users)
            draft_position = _snake_position(current_pick_number, num_users)
            draft_order = self.db.get_fantasy_league_draft_order(league_id)
            current_turn_user_id = _get_user_for_position(draft_order, draft_position)

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

    def get_available_players(
        self, league_id: FantasyLeagueID, user_id: UserID
    ) -> list[ProfessionalPlayer]:
        fantasy_league = self.fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.DRAFT]
        )
        self.fantasy_league_util.validate_membership(user_id, league_id)

        # Get players from available leagues, excluding role=none
        filters = [
            LeagueModel.id.in_(fantasy_league.available_leagues),
            ProfessionalPlayerModel.role != PlayerRole.NONE.value,
        ]
        all_players = self.db.get_players(filters)

        # Exclude already-drafted players
        existing_picks = self.db.get_draft_picks_for_league(league_id)
        drafted_player_ids = {pick.player_id for pick in existing_picks if pick.player_id}
        return [p for p in all_players if p.id not in drafted_player_ids]

    def get_available_teams(
        self, league_id: FantasyLeagueID, user_id: UserID
    ) -> list[ProfessionalTeam]:
        fantasy_league = self.fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.DRAFT]
        )
        self.fantasy_league_util.validate_membership(user_id, league_id)

        # Get teams from available leagues
        filters = [LeagueModel.id.in_(fantasy_league.available_leagues)]
        all_teams = self.db.get_teams(filters, join_league=True)

        # Exclude already-drafted teams
        existing_picks = self.db.get_draft_picks_for_league(league_id)
        drafted_team_ids = {pick.team_id for pick in existing_picks if pick.team_id}
        return [t for t in all_teams if t.id not in drafted_team_ids]

    def auto_pick(self, league_id: FantasyLeagueID, user_id: UserID) -> DraftPick:
        # Determine user's current slots
        user_teams = self.db.get_all_fantasy_teams_for_user(league_id, user_id)
        if user_teams:
            fantasy_team = user_teams[-1]
        else:
            fantasy_team = FantasyTeam(fantasy_league_id=league_id, user_id=user_id, week=0)

        # Slot priority order
        slot_roles = [
            PlayerRole.TOP,
            PlayerRole.JUNGLE,
            PlayerRole.MID,
            PlayerRole.BOTTOM,
            PlayerRole.SUPPORT,
        ]

        # Try player slots first
        available_players = self.get_available_players(league_id, user_id)
        for role in slot_roles:
            if fantasy_team.get_player_id_for_role(role) is None:
                candidates = [p for p in available_players if p.role == role]
                if candidates:
                    chosen = random.choice(candidates)
                    return self.make_pick(league_id, user_id, player_id=chosen.id)

        # All player slots filled — pick a team
        if fantasy_team.team_id is None:
            available_teams = self.get_available_teams(league_id, user_id)
            if available_teams:
                chosen_team = random.choice(available_teams)
                return self.make_pick(league_id, user_id, team_id=chosen_team.id)

        raise FantasyDraftException("No valid picks available for auto_pick")

    def _validate_and_apply_player_pick(
        self, player_id, fantasy_league, fantasy_team, existing_picks
    ) -> None:
        player = self.db.get_player_by_id(player_id)
        if player is None:
            raise FantasyDraftException(f"Player not found: {player_id}")
        if player.role == PlayerRole.NONE:
            raise FantasyDraftException(f"Player has role=none and cannot be drafted: {player_id}")

        player_league_ids = self.db.get_league_ids_for_player(player_id)
        if not any(lid in fantasy_league.available_leagues for lid in player_league_ids):
            raise FantasyDraftException(f"Player not from available leagues: {player_id}")

        for pick in existing_picks:
            if pick.player_id == player_id:
                raise FantasyDraftException(f"Player already drafted: {player_id}")

        if fantasy_team.get_player_id_for_role(player.role) is not None:
            raise FantasyDraftException(f"Role slot already filled: {player.role.value}")

        fantasy_team.set_player_id_for_role(player_id, player.role)

    def _validate_and_apply_team_pick(self, team_id, fantasy_team, existing_picks) -> None:
        team = self.db.get_team_by_id(team_id)
        if team is None:
            raise FantasyDraftException(f"Team not found: {team_id}")

        for pick in existing_picks:
            if pick.team_id == team_id:
                raise FantasyDraftException(f"Team already drafted: {team_id}")

        if fantasy_team.team_id is not None:
            raise FantasyDraftException("Team slot already filled")

        fantasy_team.team_id = team_id
