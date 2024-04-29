from typing import List

from ...db import crud
from ...db.models import (
    FantasyLeagueModel,
    ProfessionalPlayerModel
)
from ..exceptions.fantasy_league_not_found_exception import FantasyLeagueNotFoundException
from ..exceptions.fantasy_membership_exception import FantasyMembershipException
from ..exceptions.fantasy_draft_exception import FantasyDraftException
from ...riot.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from ...common.schemas.fantasy_schemas import (
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    FantasyTeam
)


class FantasyTeamService:
    @staticmethod
    def get_all_fantasy_team_weeks(fantasy_league_id: str, user_id: str) -> List[FantasyTeam]:
        validate_league(
            fantasy_league_id,
            [FantasyLeagueStatus.DRAFT, FantasyLeagueStatus.ACTIVE, FantasyLeagueStatus.COMPLETED]
        )
        validate_user_membership(user_id, fantasy_league_id)

        fantasy_team_weeks = crud.get_all_fantasy_teams_for_user(fantasy_league_id, user_id)
        fantasy_team_weeks.sort(key=lambda x: x.week)

        return fantasy_team_weeks

    @staticmethod
    def draft_player(fantasy_league_id: str, user_id: str, player_id: str) -> FantasyTeam:
        fantasy_league = validate_league(
            fantasy_league_id, [FantasyLeagueStatus.DRAFT, FantasyLeagueStatus.ACTIVE]
        )
        validate_user_membership(user_id, fantasy_league_id)
        professional_player = get_player_from_db(player_id)

        recent_fantasy_team = get_users_most_recent_fantasy_team(fantasy_league, user_id)
        if recent_fantasy_team.get_player_id_for_role(professional_player.role) is not None:
            raise FantasyDraftException(
                f"Slot not available for role ({professional_player.role}) to draft new player"
            )
        recent_fantasy_team.set_player_id_for_role(
            professional_player.id, professional_player.role
        )

        if player_already_drafted(professional_player, fantasy_league):
            raise FantasyDraftException(
                f"Player already drafted: Player ({professional_player.id}) is already drafted"
                f" in the current week"
            )

        crud.create_or_update_fantasy_team(recent_fantasy_team)
        return recent_fantasy_team

    @staticmethod
    def drop_player(fantasy_league_id: str, user_id: str, player_id: str) -> FantasyTeam:
        fantasy_league = validate_league(
            fantasy_league_id, [FantasyLeagueStatus.ACTIVE]
        )
        validate_user_membership(user_id, fantasy_league_id)
        professional_player = get_player_from_db(player_id)

        recent_fantasy_team = get_users_most_recent_fantasy_team(fantasy_league, user_id)
        if recent_fantasy_team.get_player_id_for_role(professional_player.role) \
                != professional_player.id:
            raise FantasyDraftException(
                f"Player not drafted: User {user_id} does not have player "
                f"{professional_player.id} currently drafted in fantasy league {fantasy_league_id}"
            )
        recent_fantasy_team.set_player_id_for_role(None, professional_player.role)

        crud.create_or_update_fantasy_team(recent_fantasy_team)
        return recent_fantasy_team

    @staticmethod
    def swap_players(
            fantasy_league_id: str,
            user_id: str,
            player_to_drop_id: str,
            player_to_pickup_id: str) -> FantasyTeam:
        fantasy_league = validate_league(
            fantasy_league_id, [FantasyLeagueStatus.ACTIVE]
        )
        validate_user_membership(user_id, fantasy_league_id)
        pro_player_to_drop = get_player_from_db(player_to_drop_id)
        pro_player_to_pickup = get_player_from_db(player_to_pickup_id)

        if pro_player_to_drop.role != pro_player_to_pickup.role:
            raise FantasyDraftException(
                f"Mismatching roles: Player to drop ({pro_player_to_drop.id}) does not have "
                f"the same role ({pro_player_to_drop.role}) as the player to pick "
                f"({pro_player_to_pickup.id}) with role {pro_player_to_pickup.role}"
            )

        recent_fantasy_team = get_users_most_recent_fantasy_team(fantasy_league, user_id)
        if recent_fantasy_team.get_player_id_for_role(pro_player_to_drop.role) \
                != pro_player_to_drop.id:
            raise FantasyDraftException(
                f"Player not drafted: User {user_id} does not have player "
                f"{pro_player_to_drop.id} currently drafted in fantasy league {fantasy_league_id}"
            )

        if player_already_drafted(pro_player_to_pickup, fantasy_league):
            raise FantasyDraftException(
                f"Player already drafted: Player ({pro_player_to_pickup.id}) is already drafted"
                f" in the current week"
            )

        recent_fantasy_team.set_player_id_for_role(
            pro_player_to_pickup.id, pro_player_to_pickup.role
        )

        crud.create_or_update_fantasy_team(recent_fantasy_team)
        return recent_fantasy_team


def validate_league(
        fantasy_league_id: str,
        required_states: List[FantasyLeagueStatus]) -> FantasyLeagueModel:
    fantasy_league_model = crud.get_fantasy_league_by_id(fantasy_league_id)
    if fantasy_league_model is None:
        raise FantasyLeagueNotFoundException()

    if fantasy_league_model.status not in required_states:
        raise FantasyDraftException(
            f"Invalid fantasy league state: Fantasy league ({fantasy_league_id}) is not in one of "
            f"the required states: {required_states}"
        )
    return fantasy_league_model


def validate_user_membership(user_id: str, fantasy_league_id: str):
    user_membership = crud.get_user_membership_for_fantasy_league(user_id, fantasy_league_id)
    if user_membership is None or user_membership.status != FantasyLeagueMembershipStatus.ACCEPTED:
        raise FantasyMembershipException(
            f"User ({user_id}) is not apart of the fantasy league ({fantasy_league_id})"
        )


def get_player_from_db(player_id: str) -> ProfessionalPlayerModel:
    pro_player_model = crud.get_player_by_id(player_id)
    if pro_player_model is None:
        raise ProfessionalPlayerNotFoundException()
    return pro_player_model


def get_users_most_recent_fantasy_team(
        fantasy_league: FantasyLeagueModel,
        user_id: str) -> FantasyTeam:
    fantasy_teams_by_week = crud.get_all_fantasy_teams_for_user(fantasy_league.id, user_id)
    if len(fantasy_teams_by_week) != 0:
        fantasy_teams_by_week.sort(key=lambda x: x.week)
        recent_fantasy_team = FantasyTeam.model_validate(fantasy_teams_by_week[-1])
    else:
        recent_fantasy_team = FantasyTeam(
            fantasy_league_id=fantasy_league.id,
            user_id=user_id,
            week=fantasy_league.current_week
        )
    return recent_fantasy_team


def player_already_drafted(
        professional_player: ProfessionalPlayerModel,
        fantasy_league: FantasyLeagueModel) -> bool:
    all_fantasy_teams_for_curr_week = crud.get_all_fantasy_teams_for_current_week(
        fantasy_league.id, fantasy_league.current_week
    )
    for fantasy_team_db_model in all_fantasy_teams_for_curr_week:
        fantasy_team = FantasyTeam.model_validate(fantasy_team_db_model)
        player_id_for_role = fantasy_team.get_player_id_for_role(professional_player.role)
        if player_id_for_role == professional_player.id:
            return True
    return False
