import uuid

from fantasylol.db import crud
from fantasylol.exceptions.fantasy_league_invite_exception import FantasyLeagueInviteException
from fantasylol.exceptions.fantasy_league_not_found_exception import FantasyLeagueNotFoundException
from fantasylol.exceptions.forbidden_exception import ForbiddenException
from fantasylol.exceptions.user_not_found_exception import UserNotFoundException
from fantasylol.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueSettings,
    FantasyLeagueStatus,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus
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

        create_fantasy_league_membership(
            fantasy_league_id, owner_id, FantasyLeagueMembershipStatus.ACCEPTED
        )

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

    @staticmethod
    def leave_fantasy_league(user_id: str, league_id: str):
        fantasy_league = crud.get_fantasy_league_by_id(league_id)
        if fantasy_league is None:
            raise FantasyLeagueNotFoundException()

        if fantasy_league.owner_id == user_id:
            raise FantasyLeagueInviteException("You cannot leave a fantasy league when you are the owner")

        fantasy_league_members = crud.get_pending_and_accepted_members_for_league(league_id)
        user_membership = [membership for membership in fantasy_league_members
                           if membership.user_id == user_id]
        if user_membership and user_membership[0].status == FantasyLeagueMembershipStatus.ACCEPTED:
            crud.update_fantasy_league_membership_status(
                user_membership[0], FantasyLeagueMembershipStatus.DECLINED
            )
        else:
            raise FantasyLeagueInviteException(f"You are not a member of the league: {league_id}")


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
