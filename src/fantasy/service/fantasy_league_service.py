import uuid
from typing import List

from ...db import crud
from ..exceptions.fantasy_league_invite_exception import FantasyLeagueInviteException
from ..exceptions.fantasy_league_not_found_exception import FantasyLeagueNotFoundException
from ..exceptions.forbidden_exception import ForbiddenException
from ..exceptions.user_not_found_exception import UserNotFoundException
from ..exceptions.draft_order_exception import DraftOrderException
from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueSettings,
    FantasyLeagueStatus,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    FantasyLeagueScoringSettings,
    FantasyLeagueDraftOrder,
    FantasyLeagueDraftOrderResponse
)


class FantasyLeagueService:
    def create_fantasy_league(
            self, owner_id: str, league_settings: FantasyLeagueSettings) -> FantasyLeague:
        fantasy_league_id = self.generate_new_valid_id()
        new_fantasy_league = FantasyLeague(
            id=fantasy_league_id,
            owner_id=owner_id,
            status=FantasyLeagueStatus.PRE_DRAFT,
            name=league_settings.name,
            number_of_teams=league_settings.number_of_teams
        )
        crud.create_fantasy_league(new_fantasy_league)

        fantasy_league_scoring_settings = FantasyLeagueScoringSettings(
            fantasy_league_id=fantasy_league_id
        )
        crud.create_fantasy_league_scoring_settings(fantasy_league_scoring_settings)

        create_fantasy_league_membership(
            fantasy_league_id, owner_id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_draft_order_entry(owner_id, fantasy_league_id)

        return new_fantasy_league

    @staticmethod
    def generate_new_valid_id() -> str:
        while True:
            new_id = str(uuid.uuid4())
            if not crud.get_fantasy_league_by_id(new_id):
                break
        return new_id

    @staticmethod
    def get_fantasy_league_settings(owner_id: str, league_id: str) -> FantasyLeagueSettings:
        fantasy_league_model = crud.get_fantasy_league_by_id(league_id)
        if fantasy_league_model is None:
            raise FantasyLeagueNotFoundException()
        if fantasy_league_model.owner_id != owner_id:
            raise ForbiddenException()

        league_settings = FantasyLeagueSettings(
            name=fantasy_league_model.name,
            number_of_teams=fantasy_league_model.number_of_teams
        )
        return league_settings

    @staticmethod
    def update_fantasy_league_settings(
            owner_id: str, league_id: str,
            league_settings: FantasyLeagueSettings) -> FantasyLeague:
        validate_league(owner_id, league_id)

        updated_fantasy_league_model = crud.update_fantasy_league_settings(
            league_id, league_settings
        )
        updated_fantasy_league = FantasyLeague.model_validate(updated_fantasy_league_model)
        return updated_fantasy_league

    @staticmethod
    def get_scoring_settings(owner_id: str, league_id: str) -> FantasyLeagueScoringSettings:
        validate_league(owner_id, league_id)
        scoring_settings_model = crud.get_fantasy_league_scoring_settings_by_id(league_id)
        return FantasyLeagueScoringSettings.model_validate(scoring_settings_model)

    @staticmethod
    def send_fantasy_league_invite(owner_id: str, league_id: str, username: str):
        validate_league(owner_id, league_id)
        fantasy_league_model = crud.get_fantasy_league_by_id(league_id)
        pending_and_active_members = crud.get_pending_and_accepted_members_for_league(league_id)
        if len(pending_and_active_members) >= fantasy_league_model.number_of_teams:
            raise FantasyLeagueInviteException("Invite exceeds maximum players for the league")

        user_model = crud.get_user_by_username(username)
        if user_model is None:
            raise UserNotFoundException()

        create_fantasy_league_membership(
            league_id, user_model.id, FantasyLeagueMembershipStatus.PENDING
        )

    @staticmethod
    def join_fantasy_league(user_id: str, league_id: str):
        fantasy_league = crud.get_fantasy_league_by_id(league_id)
        if fantasy_league is None:
            raise FantasyLeagueNotFoundException()

        fantasy_league_members = crud.get_pending_and_accepted_members_for_league(league_id)
        user_membership = [membership for membership in fantasy_league_members
                           if membership.user_id == user_id]
        if user_membership:
            user_membership = user_membership[0]
        else:
            raise FantasyLeagueInviteException(f"No pending invites to join league: {league_id}")

        if (user_membership.status == FantasyLeagueMembershipStatus.DECLINED or
                user_membership.status == FantasyLeagueMembershipStatus.REVOKED):
            raise FantasyLeagueInviteException(f"No pending invites to join league: {league_id}")

        accepted_member_count = 0
        for member in fantasy_league_members:
            if member.status == FantasyLeagueMembershipStatus.ACCEPTED:
                accepted_member_count += 1

        if (user_membership.status == FantasyLeagueMembershipStatus.PENDING and
                fantasy_league.number_of_teams < accepted_member_count + 1):
            raise FantasyLeagueInviteException("Fantasy league is full")

        crud.update_fantasy_league_membership_status(
            user_membership, FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_draft_order_entry(user_id, league_id)

    @staticmethod
    def leave_fantasy_league(user_id: str, league_id: str):
        fantasy_league = crud.get_fantasy_league_by_id(league_id)
        if fantasy_league is None:
            raise FantasyLeagueNotFoundException()

        if fantasy_league.owner_id == user_id:
            raise FantasyLeagueInviteException("Cannot leave a fantasy league that you own")

        fantasy_league_members = crud.get_pending_and_accepted_members_for_league(league_id)
        user_membership = [membership for membership in fantasy_league_members
                           if membership.user_id == user_id]
        if user_membership and user_membership[0].status == FantasyLeagueMembershipStatus.ACCEPTED:
            crud.update_fantasy_league_membership_status(
                user_membership[0], FantasyLeagueMembershipStatus.DECLINED
            )
            update_draft_order_on_player_leave(user_id, league_id)
        else:
            raise FantasyLeagueInviteException(f"You are not a member of the league: {league_id}")

    @staticmethod
    def get_fantasy_league_draft_order(user_id: str, league_id: str)\
            -> List[FantasyLeagueDraftOrderResponse]:
        validate_league(user_id, league_id)
        current_draft_order = crud.get_fantasy_league_draft_order(league_id)

        draft_order_response = []
        for draft_position in current_draft_order:
            user = crud.get_user_by_id(draft_position.user_id)
            new_draft_order_response = FantasyLeagueDraftOrderResponse(
                user_id=user.id, username=user.username, position=draft_position.position
            )
            draft_order_response.append(new_draft_order_response)
        return draft_order_response

    @staticmethod
    def update_fantasy_league_draft_order(
            user_id: str,
            league_id: str,
            updated_draft_order: List[FantasyLeagueDraftOrderResponse]):
        validate_league(user_id, league_id)

        current_draft_order = []
        current_draft_order_models = crud.get_fantasy_league_draft_order(league_id)
        for draft_order_model in current_draft_order_models:
            current_draft_order.append(FantasyLeagueDraftOrder.model_validate(draft_order_model))
        validate_draft_order(current_draft_order, updated_draft_order)

        for updated_position in updated_draft_order:
            db_draft_position = next((
                db_model
                for db_model in current_draft_order_models
                if db_model.user_id == updated_position.user_id), None
            )
            if db_draft_position is None:
                # This should never be hit if validation succeeds
                raise Exception("Can't find user id???")

            crud.update_fantasy_league_draft_order_position(
                db_draft_position, updated_position.position
            )


def validate_draft_order(
        current_draft_order: List[FantasyLeagueDraftOrder],
        updated_draft_order: List[FantasyLeagueDraftOrderResponse]):
    member_ids = [draft_position.user_id for draft_position in current_draft_order]

    if len(updated_draft_order) != len(current_draft_order):
        raise DraftOrderException("Draft order contains more or less players than current draft")

    for draft_order in updated_draft_order:
        if draft_order.user_id not in member_ids:
            raise DraftOrderException(f"User {draft_order.user_id} is not in current draft")

    positions = [draft_position.position for draft_position in updated_draft_order]
    positions.sort()
    expected_positions = list(range(1, len(current_draft_order) + 1))
    if positions != expected_positions:
        raise DraftOrderException("The positions given in the updated draft order are not valid")


def update_draft_order_on_player_leave(user_id: str, league_id: str):
    current_draft_order = crud.get_fantasy_league_draft_order(league_id)

    draft_position_to_delete = None
    for draft_position in current_draft_order:
        if draft_position.user_id == user_id:
            draft_position_to_delete = draft_position
            break
    if draft_position_to_delete is None:
        raise Exception(f"User {user_id} doesn't have a draft position in league {league_id}")

    crud.delete_fantasy_league_draft_order(draft_position_to_delete)
    for draft_position in current_draft_order:
        if draft_position.position > draft_position_to_delete.position:
            crud.update_fantasy_league_draft_order_position(
                draft_position, draft_position.position - 1
            )


def create_draft_order_entry(user_id: str, league_id: str):
    fantasy_league_model = crud.get_fantasy_league_by_id(league_id)
    if fantasy_league_model is None:
        raise FantasyLeagueNotFoundException()

    current_draft_order = crud.get_fantasy_league_draft_order(league_id)
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
    crud.create_fantasy_league_draft_order(new_draft_position)


def create_fantasy_league_membership(
        league_id: str, user_id: str, status: FantasyLeagueMembershipStatus):
    fantasy_league_membership = FantasyLeagueMembership(
        league_id=league_id,
        user_id=user_id,
        status=status
    )
    crud.create_fantasy_league_membership(fantasy_league_membership)


def validate_league(owner_id: str, league_id: str):
    fantasy_league_model = crud.get_fantasy_league_by_id(league_id)
    if fantasy_league_model is None:
        raise FantasyLeagueNotFoundException()
    if fantasy_league_model.owner_id != owner_id:
        raise ForbiddenException()
