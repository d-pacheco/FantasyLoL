import uuid
from typing import List, Optional

from src.db import crud

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeague,
    FantasyLeagueSettings,
    FantasyLeagueStatus,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    UsersFantasyLeagues,
    FantasyLeagueScoringSettings,
    FantasyLeagueDraftOrderResponse,
    UserID
)

from src.fantasy.exceptions import (
    FantasyLeagueInviteException,
    FantasyLeagueSettingsException,
    FantasyLeagueStartDraftException,
    ForbiddenException,
    UserNotFoundException
)

from src.fantasy.util import FantasyLeagueUtil

fantasy_league_util = FantasyLeagueUtil()


class FantasyLeagueService:
    def create_fantasy_league(
            self, owner_id: UserID, league_settings: FantasyLeagueSettings) -> FantasyLeague:
        if len(league_settings.available_leagues) > 0:
            fantasy_league_util.validate_available_leagues(league_settings.available_leagues)

        fantasy_league_id = self.generate_new_valid_id()
        new_fantasy_league = FantasyLeague(
            id=fantasy_league_id,
            owner_id=owner_id,
            status=FantasyLeagueStatus.PRE_DRAFT,
            name=league_settings.name,
            number_of_teams=league_settings.number_of_teams,
            available_leagues=league_settings.available_leagues
        )
        crud.create_fantasy_league(new_fantasy_league)

        fantasy_league_scoring_settings = FantasyLeagueScoringSettings(
            fantasy_league_id=fantasy_league_id
        )
        crud.put_fantasy_league_scoring_settings(fantasy_league_scoring_settings)

        create_fantasy_league_membership(
            fantasy_league_id, owner_id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        fantasy_league_util.create_draft_order_entry(owner_id, fantasy_league_id)

        return new_fantasy_league

    @staticmethod
    def generate_new_valid_id() -> FantasyLeagueID:
        while True:
            new_id = FantasyLeagueID(str(uuid.uuid4()))
            if not crud.get_fantasy_league_by_id(new_id):
                break
        return new_id

    @staticmethod
    def get_fantasy_league_settings(
            owner_id: UserID,
            league_id: FantasyLeagueID) -> FantasyLeagueSettings:
        fantasy_league_model = fantasy_league_util.validate_league(league_id)
        if fantasy_league_model.owner_id != owner_id:
            raise ForbiddenException()

        league_settings = FantasyLeagueSettings(
            name=fantasy_league_model.name,
            number_of_teams=fantasy_league_model.number_of_teams,
            available_leagues=fantasy_league_model.available_leagues
        )
        return league_settings

    @staticmethod
    def update_fantasy_league_settings(
            owner_id: UserID,
            league_id: FantasyLeagueID,
            updated_league_settings: FantasyLeagueSettings) -> FantasyLeagueSettings:
        fantasy_league_model = fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.PRE_DRAFT]
        )
        if fantasy_league_model.owner_id != owner_id:
            raise ForbiddenException()

        fantasy_league_members = crud.get_pending_and_accepted_members_for_league(league_id)
        accepted_member_count = 0
        for member in fantasy_league_members:
            if member.status == FantasyLeagueMembershipStatus.ACCEPTED:
                accepted_member_count += 1
        if updated_league_settings.number_of_teams < accepted_member_count:
            raise FantasyLeagueSettingsException(
                f"Can not reduce number of teams to be less than the current number of active"
                f"members inside of the fantasy league ({accepted_member_count})"
            )

        if len(updated_league_settings.available_leagues) > 0:
            fantasy_league_util.validate_available_leagues(
                updated_league_settings.available_leagues
            )

        updated_fantasy_league = crud.update_fantasy_league_settings(
            league_id, updated_league_settings
        )
        updated_fantasy_league_settings = FantasyLeagueSettings(
            name=updated_fantasy_league.name,
            number_of_teams=updated_fantasy_league.number_of_teams,
            available_leagues=updated_league_settings.available_leagues
        )
        return updated_fantasy_league_settings

    @staticmethod
    def get_scoring_settings(
            owner_id: UserID,
            league_id: FantasyLeagueID) -> FantasyLeagueScoringSettings:
        fantasy_league_model = fantasy_league_util.validate_league(league_id)
        if fantasy_league_model.owner_id != owner_id:
            raise ForbiddenException()
        scoring_settings = crud.get_fantasy_league_scoring_settings_by_id(league_id)
        assert (scoring_settings is not None)
        return scoring_settings

    @staticmethod
    def update_scoring_settings(
            fantasy_league_id: FantasyLeagueID,
            user_id: UserID,
            scoring_settings: FantasyLeagueScoringSettings) -> FantasyLeagueScoringSettings:
        fantasy_league = fantasy_league_util.validate_league(
            fantasy_league_id, [FantasyLeagueStatus.PRE_DRAFT]
        )
        if fantasy_league.owner_id != user_id:
            raise ForbiddenException()

        # Ensure that fantasy_league_id for the scoring settings is the one called by the endpoint
        scoring_settings.fantasy_league_id = fantasy_league_id
        crud.put_fantasy_league_scoring_settings(scoring_settings)
        return scoring_settings

    @staticmethod
    def get_users_pending_and_accepted_fantasy_leagues(user_id: UserID) -> UsersFantasyLeagues:
        pending_fantasy_leagues = crud.get_users_fantasy_leagues_with_membership_status(
            user_id, FantasyLeagueMembershipStatus.PENDING
        )
        accepted_fantasy_leagues = crud.get_users_fantasy_leagues_with_membership_status(
            user_id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        users_fantasy_leagues = UsersFantasyLeagues(
            pending=pending_fantasy_leagues,
            accepted=accepted_fantasy_leagues
        )
        return users_fantasy_leagues

    @staticmethod
    def send_fantasy_league_invite(
            owner_id: UserID, league_id: FantasyLeagueID, username: str) -> None:
        fantasy_league_model = fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.PRE_DRAFT]
        )
        if fantasy_league_model.owner_id != owner_id:
            raise ForbiddenException()

        pending_and_active_members = crud.get_pending_and_accepted_members_for_league(league_id)
        if len(pending_and_active_members) >= fantasy_league_model.number_of_teams:
            raise FantasyLeagueInviteException("Invite exceeds maximum players for the league")

        user = crud.get_user_by_username(username)
        if user is None:
            raise UserNotFoundException()

        create_fantasy_league_membership(league_id, user.id, FantasyLeagueMembershipStatus.PENDING)

    @staticmethod
    def join_fantasy_league(user_id: UserID, league_id: FantasyLeagueID) -> None:
        fantasy_league_model = fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.PRE_DRAFT]
        )

        user_membership: Optional[FantasyLeagueMembership] = None
        accepted_member_count = 0
        fantasy_league_members = crud.get_pending_and_accepted_members_for_league(league_id)
        for membership in fantasy_league_members:
            if membership.status == FantasyLeagueMembershipStatus.ACCEPTED:
                accepted_member_count += 1
            if membership.user_id == user_id:
                user_membership = membership

        if (user_membership is None or
                user_membership.status == FantasyLeagueMembershipStatus.DECLINED or
                user_membership.status == FantasyLeagueMembershipStatus.REVOKED):
            raise FantasyLeagueInviteException(f"No pending invites to join league: {league_id}")

        if (user_membership.status == FantasyLeagueMembershipStatus.PENDING and
                fantasy_league_model.number_of_teams < accepted_member_count + 1):
            raise FantasyLeagueInviteException("Fantasy league is full")

        crud.update_fantasy_league_membership_status(
            user_membership, FantasyLeagueMembershipStatus.ACCEPTED
        )
        fantasy_league_util.create_draft_order_entry(user_id, league_id)

    @staticmethod
    def leave_fantasy_league(user_id: UserID, league_id: FantasyLeagueID) -> None:
        fantasy_league_model = fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.PRE_DRAFT]
        )

        if fantasy_league_model.owner_id == user_id:
            raise FantasyLeagueInviteException("Cannot leave a fantasy league that you own")

        user_membership = crud.get_user_membership_for_fantasy_league(user_id, league_id)
        if user_membership and user_membership.status == FantasyLeagueMembershipStatus.ACCEPTED:
            crud.update_fantasy_league_membership_status(
                user_membership, FantasyLeagueMembershipStatus.DECLINED
            )
            fantasy_league_util.update_draft_order_on_player_leave(user_id, league_id)
        else:
            raise FantasyLeagueInviteException(f"You are not a member of the league: {league_id}")

    @staticmethod
    def revoke_from_fantasy_league(
            fantasy_league_id: FantasyLeagueID,
            user_id: UserID,
            user_to_remove_id: UserID) -> None:
        fantasy_league = fantasy_league_util.validate_league(
            fantasy_league_id, [FantasyLeagueStatus.PRE_DRAFT]
        )
        if fantasy_league.owner_id != user_id:
            raise ForbiddenException()

        if user_id == user_to_remove_id:
            raise FantasyLeagueInviteException(
                "Invalid revoke request: You cannot revoke your own membership"
            )

        user_to_remove_membership = crud.get_user_membership_for_fantasy_league(
            user_to_remove_id, fantasy_league_id
        )
        if user_to_remove_membership is None or \
                user_to_remove_membership.status != FantasyLeagueMembershipStatus.ACCEPTED:
            raise FantasyLeagueInviteException(
                f"No accepted membership: User {user_to_remove_id} does not have an accepted "
                f"membership to the fantasy league {fantasy_league_id}"
            )

        crud.update_fantasy_league_membership_status(
            user_to_remove_membership, FantasyLeagueMembershipStatus.REVOKED
        )
        fantasy_league_util.update_draft_order_on_player_leave(user_to_remove_id, fantasy_league_id)

    @staticmethod
    def get_fantasy_league_draft_order(
            user_id: UserID,
            league_id: FantasyLeagueID) -> List[FantasyLeagueDraftOrderResponse]:
        fantasy_league_model = fantasy_league_util.validate_league(league_id)
        if fantasy_league_model.owner_id != user_id:
            raise ForbiddenException()

        draft_order_response = []
        current_draft_order = crud.get_fantasy_league_draft_order(league_id)
        for draft_position in current_draft_order:
            user = crud.get_user_by_id(draft_position.user_id)
            if user is None:
                raise UserNotFoundException()
            new_draft_order_response = FantasyLeagueDraftOrderResponse(
                user_id=user.id, username=user.username, position=draft_position.position
            )
            draft_order_response.append(new_draft_order_response)
        return draft_order_response

    @staticmethod
    def update_fantasy_league_draft_order(
            user_id: UserID,
            league_id: FantasyLeagueID,
            updated_draft_order: List[FantasyLeagueDraftOrderResponse]) -> None:
        fantasy_league_model = fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.PRE_DRAFT]
        )
        if fantasy_league_model.owner_id != user_id:
            raise ForbiddenException()

        current_draft_order = crud.get_fantasy_league_draft_order(league_id)
        fantasy_league_util.validate_draft_order(current_draft_order, updated_draft_order)

        for updated_position in updated_draft_order:
            db_draft_position = next((
                db_model
                for db_model in current_draft_order
                if db_model.user_id == updated_position.user_id), None
            )
            if db_draft_position is None:
                # This should never be hit if validation succeeds
                raise Exception("Can't find user id???")

            crud.update_fantasy_league_draft_order_position(
                db_draft_position, updated_position.position
            )

    @staticmethod
    def start_fantasy_draft(user_id: UserID, fantasy_league_id: FantasyLeagueID) -> None:
        fantasy_league = fantasy_league_util.validate_league(
            fantasy_league_id, [FantasyLeagueStatus.PRE_DRAFT]
        )
        if fantasy_league.owner_id != user_id:
            raise ForbiddenException()

        pending_and_accepted_memberships = crud.get_pending_and_accepted_members_for_league(
            fantasy_league_id
        )
        accepted_count = 0
        for membership in pending_and_accepted_memberships:
            if membership.status == FantasyLeagueMembershipStatus.ACCEPTED:
                accepted_count += 1
        if accepted_count != fantasy_league.number_of_teams:
            raise FantasyLeagueStartDraftException(
                f"Invalid member count: The fantasy league with ID {fantasy_league_id} does not "
                f"have correct number of members to start the draft. "
                f"Expected {fantasy_league.number_of_teams} but has {accepted_count}."
            )

        if len(fantasy_league.available_leagues) == 0:
            raise FantasyLeagueStartDraftException(
                f"Available leagues not set: The fantasy league with ID {fantasy_league_id} must "
                f"have one Riot league set for players to draft from before starting the draft."
            )

        crud.update_fantasy_league_status(fantasy_league_id, FantasyLeagueStatus.DRAFT)
        crud.update_fantasy_league_current_draft_position(fantasy_league_id, 1)


def create_fantasy_league_membership(
        league_id: FantasyLeagueID,
        user_id: UserID,
        status: FantasyLeagueMembershipStatus) -> None:
    fantasy_league_membership = FantasyLeagueMembership(
        league_id=league_id,
        user_id=user_id,
        status=status
    )
    crud.create_fantasy_league_membership(fantasy_league_membership)
