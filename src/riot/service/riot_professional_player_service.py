import logging

from sqlalchemy import or_

from src.common.schemas.search_parameters import PlayerSearchParameters
from src.common.schemas.riot_data_schemas import (
    ProfessionalPlayer,
    ProPlayerID,
    PlayerMatchHistoryEntry,
    PlayerCareerSummary,
)
from src.db.database_service import DatabaseService
from src.db.models import ProfessionalPlayerModel, ProfessionalTeamModel, LeagueModel
from src.common.exceptions import ProfessionalPlayerNotFoundException

logger = logging.getLogger("api.riot")


def _avg(total: float, count: int) -> float:
    return round(total / count, 2) if count else 0.0


def _rate_per_min(total: int, total_seconds: int) -> float:
    return round(total / (total_seconds / 60), 2) if total_seconds else 0.0


class RiotProfessionalPlayerService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_players(self, search_parameters: PlayerSearchParameters) -> list[ProfessionalPlayer]:
        filters: list = []
        if search_parameters.summoner_name is not None:
            filters.append(
                ProfessionalPlayerModel.summoner_name.ilike(f"%{search_parameters.summoner_name}%")
            )
        if search_parameters.team_name is not None:
            term = f"%{search_parameters.team_name}%"
            filters.append(
                or_(
                    ProfessionalTeamModel.name.ilike(term),
                    ProfessionalTeamModel.code.ilike(term),
                )
            )
        if search_parameters.role is not None:
            filters.append(ProfessionalPlayerModel.role == search_parameters.role)
        if search_parameters.fantasy_available is not None:
            filters.append(LeagueModel.fantasy_available == search_parameters.fantasy_available)
        if search_parameters.active_only:
            filters.append(ProfessionalTeamModel.status == "active")

        professional_players = self.db.get_players(filters)
        return professional_players

    def get_player_by_id(self, professional_player_id: ProPlayerID) -> ProfessionalPlayer:
        professional_player = self.db.get_player_by_id(professional_player_id)
        if professional_player is None:
            raise ProfessionalPlayerNotFoundException()
        return professional_player

    def get_player_match_history(
        self, professional_player_id: ProPlayerID
    ) -> list[PlayerMatchHistoryEntry]:
        # Validate the player exists (raises 404 via the endpoint handler otherwise).
        self.get_player_by_id(professional_player_id)
        return self.db.get_player_match_history(professional_player_id)

    def get_player_career_summary(self, professional_player_id: ProPlayerID) -> PlayerCareerSummary:
        self.get_player_by_id(professional_player_id)
        entries = self.db.get_player_match_history(professional_player_id)

        games = len(entries)
        summary = PlayerCareerSummary(player_id=professional_player_id, games_played=games)
        if games == 0:
            return summary

        total_kills = sum(e.kills for e in entries)
        total_deaths = sum(e.deaths for e in entries)
        total_assists = sum(e.assists for e in entries)
        total_cs = sum(e.creep_score for e in entries)
        total_gold = sum(e.total_gold for e in entries)
        total_seconds = sum(e.duration_seconds or 0 for e in entries)
        decided = [e for e in entries if e.win is not None]
        wins = sum(1 for e in decided if e.win)

        multi_counts = {"double": 0, "triple": 0, "quadra": 0, "penta": 0}
        for e in entries:
            for mk in e.multi_kills:
                if mk in multi_counts:
                    multi_counts[mk] += 1

        summary.avg_kills = _avg(total_kills, games)
        summary.avg_deaths = _avg(total_deaths, games)
        summary.avg_assists = _avg(total_assists, games)
        summary.kda_ratio = round((total_kills + total_assists) / max(total_deaths, 1), 2)
        summary.avg_creep_score = _avg(total_cs, games)
        summary.cs_per_min = _rate_per_min(total_cs, total_seconds)
        summary.avg_total_gold = _avg(total_gold, games)
        summary.gold_per_min = _rate_per_min(total_gold, total_seconds)
        summary.avg_kill_participation = _avg(sum(e.kill_participation for e in entries), games)
        summary.avg_damage_share = _avg(sum(e.champion_damage_share for e in entries), games)
        summary.avg_wards_placed = _avg(sum(e.wards_placed for e in entries), games)
        summary.avg_wards_destroyed = _avg(sum(e.wards_destroyed for e in entries), games)
        summary.win_rate = round(100 * wins / len(decided), 2) if decided else 0.0
        summary.double_kills = multi_counts["double"]
        summary.triple_kills = multi_counts["triple"]
        summary.quadra_kills = multi_counts["quadra"]
        summary.penta_kills = multi_counts["penta"]
        return summary
