from typing import List

from ...db import crud

from ...common.schemas.riot_data_schemas import ProfessionalPlayer, ProPlayerID
from ...common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueID,
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    FantasyTeam,
    UserID
)

from ...riot.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException

from ..exceptions.fantasy_membership_exception import FantasyMembershipException
from ..exceptions.fantasy_draft_exception import FantasyDraftException
from ..util.fantasy_league_util import FantasyLeagueUtil
from ..util.fantasty_team_util import FantasyTeamUtil

fantasy_league_util = FantasyLeagueUtil()
fantasy_team_util = FantasyTeamUtil()


class FantasyTeamService:
    @staticmethod
    def get_all_fantasy_team_weeks(
            fantasy_league_id: FantasyLeagueID,
            user_id: UserID
    ) -> List[FantasyTeam]:
        fantasy_league_util.validate_league(
            fantasy_league_id,
            [FantasyLeagueStatus.DRAFT, FantasyLeagueStatus.ACTIVE, FantasyLeagueStatus.COMPLETED]
        )
        validate_user_membership(user_id, fantasy_league_id)

        fantasy_team_weeks = crud.get_all_fantasy_teams_for_user(fantasy_league_id, user_id)
        fantasy_team_weeks.sort(key=lambda x: x.week)

        return fantasy_team_weeks

    @staticmethod
    def pickup_player(
            fantasy_league_id: FantasyLeagueID,
            user_id: UserID,
            player_id: ProPlayerID
    ) -> FantasyTeam:
        fantasy_league = fantasy_league_util.validate_league(
            fantasy_league_id, [FantasyLeagueStatus.DRAFT, FantasyLeagueStatus.ACTIVE]
        )
        professional_player = get_player_from_db(player_id)
        fantasy_team_util.validate_player_from_available_league(fantasy_league, player_id)
        validate_user_membership(user_id, fantasy_league_id)

        if (fantasy_league.status == FantasyLeagueStatus.DRAFT) \
                and not (fantasy_team_util.is_users_position_to_draft(fantasy_league, user_id)):
            raise FantasyDraftException(
                f"Invalid user draft position: The draft position for the user "
                f"with ID {user_id} is not the current draft position for fantasy league "
                f"with ID {fantasy_league_id}"
            )

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

        crud.put_fantasy_team(recent_fantasy_team)
        if fantasy_league.status == FantasyLeagueStatus.DRAFT:
            fantasy_league_util.update_fantasy_leagues_current_draft_position(fantasy_league)
            if fantasy_team_util.all_teams_fully_drafted(fantasy_league):
                crud.update_fantasy_league_status(fantasy_league_id, FantasyLeagueStatus.ACTIVE)
                # TODO: NEED TO SET THE CURRENT WEEK TO BE THE CURRENT WEEK FOR THE LEAGUE(S)

        return recent_fantasy_team

    @staticmethod
    def drop_player(
            fantasy_league_id: FantasyLeagueID,
            user_id: UserID, player_id: ProPlayerID
    ) -> FantasyTeam:
        fantasy_league = fantasy_league_util.validate_league(
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

        crud.put_fantasy_team(recent_fantasy_team)
        return recent_fantasy_team

    @staticmethod
    def swap_players(
            fantasy_league_id: FantasyLeagueID,
            user_id: UserID,
            player_to_drop_id: ProPlayerID,
            player_to_pickup_id: ProPlayerID
    ) -> FantasyTeam:
        fantasy_league = fantasy_league_util.validate_league(
            fantasy_league_id, [FantasyLeagueStatus.ACTIVE]
        )
        validate_user_membership(user_id, fantasy_league_id)
        pro_player_to_drop = get_player_from_db(player_to_drop_id)
        pro_player_to_pickup = get_player_from_db(player_to_pickup_id)
        fantasy_team_util.validate_player_from_available_league(fantasy_league, player_to_pickup_id)

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

        crud.put_fantasy_team(recent_fantasy_team)
        return recent_fantasy_team


def validate_user_membership(user_id: UserID, fantasy_league_id: FantasyLeagueID) -> None:
    user_membership = crud.get_user_membership_for_fantasy_league(user_id, fantasy_league_id)
    if user_membership is None or user_membership.status != FantasyLeagueMembershipStatus.ACCEPTED:
        raise FantasyMembershipException(
            f"User ({user_id}) is not apart of the fantasy league ({fantasy_league_id})"
        )


def get_player_from_db(player_id: ProPlayerID) -> ProfessionalPlayer:
    pro_player = crud.get_player_by_id(player_id)
    if pro_player is None:
        raise ProfessionalPlayerNotFoundException()
    return pro_player


def get_users_most_recent_fantasy_team(
        fantasy_league: FantasyLeague,
        user_id: UserID) -> FantasyTeam:
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
        professional_player: ProfessionalPlayer,
        fantasy_league: FantasyLeague) -> bool:
    all_fantasy_teams_for_curr_week = crud.get_all_fantasy_teams_for_week(
        fantasy_league.id, fantasy_league.current_week
    )
    for fantasy_team_db_model in all_fantasy_teams_for_curr_week:
        fantasy_team = FantasyTeam.model_validate(fantasy_team_db_model)
        player_id_for_role = fantasy_team.get_player_id_for_role(professional_player.role)
        if player_id_for_role == professional_player.id:
            return True
    return False
