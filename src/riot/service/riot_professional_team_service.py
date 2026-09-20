import logging

from sqlalchemy import or_

from src.common.schemas.search_parameters import TeamSearchParameters
from src.common.schemas.riot_data_schemas import (
    ProfessionalTeam,
    ProTeamID,
    ProfessionalPlayer,
    PlayerRole,
    TeamMatchHistoryEntry,
    TeamSummary,
)
from src.db.database_service import DatabaseService
from src.db.models import ProfessionalTeamModel, LeagueModel, ProfessionalPlayerModel
from src.riot.exceptions import ProfessionalTeamNotFoundException

logger = logging.getLogger("api.riot")

_ROLE_ORDER = {
    PlayerRole.TOP: 0,
    PlayerRole.JUNGLE: 1,
    PlayerRole.MID: 2,
    PlayerRole.BOTTOM: 3,
    PlayerRole.SUPPORT: 4,
    PlayerRole.NONE: 5,
}


def _avg(total: float, count: int) -> float:
    return round(total / count, 2) if count else 0.0


class RiotProfessionalTeamService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_teams(self, search_parameters: TeamSearchParameters) -> list[ProfessionalTeam]:
        filters: list = []
        join_league = False

        if search_parameters.search is not None:
            term = f"%{search_parameters.search}%"
            filters.append(
                or_(
                    ProfessionalTeamModel.name.ilike(term),
                    ProfessionalTeamModel.code.ilike(term),
                )
            )
        if search_parameters.slug is not None:
            filters.append(ProfessionalTeamModel.slug == search_parameters.slug)
        if search_parameters.name is not None:
            filters.append(ProfessionalTeamModel.name.ilike(f"%{search_parameters.name}%"))
        if search_parameters.code is not None:
            filters.append(ProfessionalTeamModel.code.ilike(f"%{search_parameters.code}%"))
        if search_parameters.status is not None:
            filters.append(ProfessionalTeamModel.status == search_parameters.status)
        if search_parameters.league is not None:
            filters.append(
                ProfessionalTeamModel.home_league_name.ilike(f"%{search_parameters.league}%")
            )
        if search_parameters.fantasy_available is not None:
            join_league = True
            filters.append(LeagueModel.fantasy_available == search_parameters.fantasy_available)
        if search_parameters.active_only:
            filters.append(ProfessionalTeamModel.status == "active")
        if search_parameters.has_players:
            filters.append(ProfessionalTeamModel.id.in_(self.db.get_team_ids_with_players()))

        return self.db.get_teams(filters, join_league=join_league)

    def get_team_by_id(self, professional_team_id: ProTeamID) -> ProfessionalTeam:
        professional_team = self.db.get_team_by_id(professional_team_id)
        if professional_team is None:
            raise ProfessionalTeamNotFoundException()
        return professional_team

    def get_team_roster(self, professional_team_id: ProTeamID) -> list[ProfessionalPlayer]:
        self.get_team_by_id(professional_team_id)
        players = self.db.get_players([ProfessionalPlayerModel.team_id == professional_team_id])
        return sorted(players, key=lambda p: (_ROLE_ORDER.get(p.role, 99), p.summoner_name or ""))

    def get_team_match_history(
        self, professional_team_id: ProTeamID
    ) -> list[TeamMatchHistoryEntry]:
        self.get_team_by_id(professional_team_id)
        return self.db.get_team_match_history(professional_team_id)

    def get_team_summary(self, professional_team_id: ProTeamID) -> TeamSummary:
        self.get_team_by_id(professional_team_id)
        matches = self.db.get_team_match_history(professional_team_id)
        stat_lines = self.db.get_team_game_stat_lines(professional_team_id)

        wins = sum(1 for m in matches if m.win is True)
        losses = sum(1 for m in matches if m.win is False)
        decided = wins + losses
        games = len(stat_lines)

        return TeamSummary(
            team_id=professional_team_id,
            matches_played=len(matches),
            wins=wins,
            losses=losses,
            win_rate=round(100 * wins / decided, 2) if decided else 0.0,
            games_counted=games,
            avg_kills=_avg(sum(s["total_kills"] for s in stat_lines), games),
            avg_gold=_avg(sum(s["total_gold"] for s in stat_lines), games),
            avg_towers=_avg(sum(s["towers"] for s in stat_lines), games),
            avg_barons=_avg(sum(s["barons"] for s in stat_lines), games),
            avg_inhibitors=_avg(sum(s["inhibitors"] for s in stat_lines), games),
            avg_dragons=_avg(sum(s["dragons"] for s in stat_lines), games),
        )
