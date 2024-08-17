from typing import List

from src.db.database_service import DatabaseService
from src.common.schemas.riot_data_schemas import ProfessionalPlayer, ProPlayerID
from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueID,
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    FantasyTeam,
    UserID
)
from src.common.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from src.fantasy.exceptions import FantasyMembershipException, FantasyDraftException
from src.fantasy.util import FantasyTeamUtil, FantasyLeagueUtil


class FantasyTeamService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        self.fantasy_league_util = FantasyLeagueUtil(database_service)
        self.fantasy_team_util = FantasyTeamUtil(database_service)

    def get_all_fantasy_team_weeks(
            self,
            fantasy_league_id: FantasyLeagueID,
            user_id: UserID
    ) -> List[FantasyTeam]:
        self.fantasy_league_util.validate_league(
            fantasy_league_id,
            [FantasyLeagueStatus.DRAFT, FantasyLeagueStatus.ACTIVE, FantasyLeagueStatus.COMPLETED]
        )
        self.validate_user_membership(user_id, fantasy_league_id)

        fantasy_team_weeks = self.db.get_all_fantasy_teams_for_user(fantasy_league_id, user_id)
        fantasy_team_weeks.sort(key=lambda x: x.week)

        return fantasy_team_weeks

    def pickup_player(
            self,
            fantasy_league_id: FantasyLeagueID,
            user_id: UserID,
            player_id: ProPlayerID
    ) -> FantasyTeam:
        fantasy_league = self.fantasy_league_util.validate_league(
            fantasy_league_id, [FantasyLeagueStatus.DRAFT, FantasyLeagueStatus.ACTIVE]
        )
        professional_player = self.get_player_from_db(player_id)
        self.fantasy_team_util.validate_player_from_available_league(fantasy_league, player_id)
        self.validate_user_membership(user_id, fantasy_league_id)

        if (fantasy_league.status == FantasyLeagueStatus.DRAFT) \
                and not self.fantasy_team_util.is_users_position_to_draft(fantasy_league, user_id):
            raise FantasyDraftException(
                f"Invalid user draft position: The draft position for the user "
                f"with ID {user_id} is not the current draft position for fantasy league "
                f"with ID {fantasy_league_id}"
            )

        recent_fantasy_team = self.get_users_most_recent_fantasy_team(fantasy_league, user_id)
        if recent_fantasy_team.get_player_id_for_role(professional_player.role) is not None:
            raise FantasyDraftException(
                f"Slot not available for role ({professional_player.role}) to draft new player"
            )
        recent_fantasy_team.set_player_id_for_role(
            professional_player.id, professional_player.role
        )

        if self.player_already_drafted(professional_player, fantasy_league):
            raise FantasyDraftException(
                f"Player already drafted: Player ({professional_player.id}) is already drafted"
                f" in the current week"
            )

        self.db.put_fantasy_team(recent_fantasy_team)
        if fantasy_league.status == FantasyLeagueStatus.DRAFT:
            self.fantasy_league_util.update_fantasy_leagues_current_draft_position(fantasy_league)
            if self.fantasy_team_util.all_teams_fully_drafted(fantasy_league):
                self.db.update_fantasy_league_status(fantasy_league_id, FantasyLeagueStatus.ACTIVE)
                # TODO: NEED TO SET THE CURRENT WEEK TO BE THE CURRENT WEEK FOR THE LEAGUE(S)

        return recent_fantasy_team

    def drop_player(
            self,
            fantasy_league_id: FantasyLeagueID,
            user_id: UserID, player_id: ProPlayerID
    ) -> FantasyTeam:
        fantasy_league = self.fantasy_league_util.validate_league(
            fantasy_league_id, [FantasyLeagueStatus.ACTIVE]
        )
        self.validate_user_membership(user_id, fantasy_league_id)
        professional_player = self.get_player_from_db(player_id)

        recent_fantasy_team = self.get_users_most_recent_fantasy_team(fantasy_league, user_id)
        if recent_fantasy_team.get_player_id_for_role(professional_player.role) \
                != professional_player.id:
            raise FantasyDraftException(
                f"Player not drafted: User {user_id} does not have player "
                f"{professional_player.id} currently drafted in fantasy league {fantasy_league_id}"
            )
        recent_fantasy_team.set_player_id_for_role(None, professional_player.role)

        self.db.put_fantasy_team(recent_fantasy_team)
        return recent_fantasy_team

    def swap_players(
            self,
            fantasy_league_id: FantasyLeagueID,
            user_id: UserID,
            player_to_drop_id: ProPlayerID,
            player_to_pickup_id: ProPlayerID
    ) -> FantasyTeam:
        fantasy_league = self.fantasy_league_util.validate_league(
            fantasy_league_id, [FantasyLeagueStatus.ACTIVE]
        )
        self.validate_user_membership(user_id, fantasy_league_id)
        pro_player_to_drop = self.get_player_from_db(player_to_drop_id)
        pro_player_to_pickup = self.get_player_from_db(player_to_pickup_id)
        self.fantasy_team_util.validate_player_from_available_league(
            fantasy_league, player_to_pickup_id)

        if pro_player_to_drop.role != pro_player_to_pickup.role:
            raise FantasyDraftException(
                f"Mismatching roles: Player to drop ({pro_player_to_drop.id}) does not have "
                f"the same role ({pro_player_to_drop.role}) as the player to pick "
                f"({pro_player_to_pickup.id}) with role {pro_player_to_pickup.role}"
            )

        recent_fantasy_team = self.get_users_most_recent_fantasy_team(fantasy_league, user_id)
        if recent_fantasy_team.get_player_id_for_role(pro_player_to_drop.role) \
                != pro_player_to_drop.id:
            raise FantasyDraftException(
                f"Player not drafted: User {user_id} does not have player "
                f"{pro_player_to_drop.id} currently drafted in fantasy league {fantasy_league_id}"
            )

        if self.player_already_drafted(pro_player_to_pickup, fantasy_league):
            raise FantasyDraftException(
                f"Player already drafted: Player ({pro_player_to_pickup.id}) is already drafted"
                f" in the current week"
            )

        recent_fantasy_team.set_player_id_for_role(
            pro_player_to_pickup.id, pro_player_to_pickup.role
        )

        self.db.put_fantasy_team(recent_fantasy_team)
        return recent_fantasy_team

    def validate_user_membership(self, user_id: UserID, fantasy_league_id: FantasyLeagueID) -> None:
        user_membership = self.db.get_user_membership_for_fantasy_league(user_id, fantasy_league_id)
        if user_membership is None or \
                user_membership.status != FantasyLeagueMembershipStatus.ACCEPTED:
            raise FantasyMembershipException(
                f"User ({user_id}) is not apart of the fantasy league ({fantasy_league_id})"
            )

    def get_player_from_db(self, player_id: ProPlayerID) -> ProfessionalPlayer:
        pro_player = self.db.get_player_by_id(player_id)
        if pro_player is None:
            raise ProfessionalPlayerNotFoundException()
        return pro_player

    def get_users_most_recent_fantasy_team(
            self,
            fantasy_league: FantasyLeague,
            user_id: UserID) -> FantasyTeam:
        fantasy_teams_by_week = self.db.get_all_fantasy_teams_for_user(fantasy_league.id, user_id)
        if len(fantasy_teams_by_week) != 0:
            fantasy_teams_by_week.sort(key=lambda x: x.week)
            recent_fantasy_team = FantasyTeam.model_validate(fantasy_teams_by_week[-1])
        else:
            current_week = fantasy_league.current_week \
                if fantasy_league.current_week is not None else 0
            recent_fantasy_team = FantasyTeam(
                fantasy_league_id=fantasy_league.id,
                user_id=user_id,
                week=current_week
            )
        return recent_fantasy_team

    def player_already_drafted(
            self,
            professional_player: ProfessionalPlayer,
            fantasy_league: FantasyLeague) -> bool:
        assert (fantasy_league.current_week is not None)
        all_fantasy_teams_for_curr_week = self.db.get_all_fantasy_teams_for_week(
            fantasy_league.id, fantasy_league.current_week
        )
        for fantasy_team_db_model in all_fantasy_teams_for_curr_week:
            fantasy_team = FantasyTeam.model_validate(fantasy_team_db_model)
            player_id_for_role = fantasy_team.get_player_id_for_role(professional_player.role)
            if player_id_for_role == professional_player.id:
                return True
        return False
