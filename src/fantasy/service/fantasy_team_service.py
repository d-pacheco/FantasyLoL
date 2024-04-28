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
    def draft_player(fantasy_league_id: str, user_id: str, player_id: str) -> FantasyTeam:
        fantasy_league = validate_league(
            fantasy_league_id,
            [FantasyLeagueStatus.DRAFT, FantasyLeagueStatus.ACTIVE]
        )
        validate_user_membership(user_id, fantasy_league_id)
        professional_player = get_player_from_db(player_id)

        current_fantasy_team = validate_user_can_draft_player_for_role(
            fantasy_league, user_id, professional_player
        )
        current_fantasy_team.set_player_id_for_role(
            professional_player.id, professional_player.role
        )

        if player_already_drafted(professional_player, fantasy_league):
            raise FantasyDraftException(
                f"Player ({professional_player.id}) is already drafted in the current week"
            )

        crud.create_or_update_fantasy_team(current_fantasy_team)
        return current_fantasy_team


def validate_league(
        fantasy_league_id: str,
        required_states: List[FantasyLeagueStatus]) -> FantasyLeagueModel:
    fantasy_league_model = crud.get_fantasy_league_by_id(fantasy_league_id)
    if fantasy_league_model is None:
        raise FantasyLeagueNotFoundException()

    if fantasy_league_model.status not in required_states:
        raise FantasyDraftException(
            f"Fantasy league ({fantasy_league_id}) is not in one of the required states: "
            f"{required_states}"
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


def validate_user_can_draft_player_for_role(
        fantasy_league: FantasyLeagueModel,
        user_id: str,
        professional_player: ProfessionalPlayerModel) -> FantasyTeam:
    fantasy_teams_by_week = crud.get_all_fantasy_teams_for_user(fantasy_league.id, user_id)
    if len(fantasy_teams_by_week) > 1:
        fantasy_teams_by_week.sort(key=lambda x: x.week)
        recent_fantasy_team = FantasyTeam.model_validate(fantasy_teams_by_week[-1])
        if recent_fantasy_team.get_player_id_for_role(professional_player.role) is not None:
            raise FantasyDraftException(
                f"Slot not available for role ({professional_player.role}) to draft new player"
            )
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
