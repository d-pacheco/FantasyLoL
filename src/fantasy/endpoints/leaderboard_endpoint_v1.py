from fastapi import Depends
from classy_fastapi import Routable, get

from src.auth import AuthPrincipal, JWTBearer, Permissions
from src.common.schemas.fantasy_schemas import FantasyLeagueID
from src.fantasy.service.leaderboard_service import LeaderboardService


class LeaderboardEndpoint(Routable):
    def __init__(self, leaderboard_service: LeaderboardService):
        super().__init__()
        self.__leaderboard_service = leaderboard_service

    @get(
        path="/leagues/{fantasy_league_id}/leaderboard",
        description="Get the leaderboard for a fantasy league. "
        "The caller must be an accepted member of the league.",
        tags=["Fantasy Leaderboard"],
    )
    def get_leaderboard(
        self,
        fantasy_league_id: FantasyLeagueID,
        principal: AuthPrincipal = Depends(JWTBearer([Permissions.FANTASY_READ])),
    ) -> dict:
        return self.__leaderboard_service.get_leaderboard(fantasy_league_id, principal.user_id)

    @get(
        path="/leagues/{fantasy_league_id}/scores",
        description="Get detailed scoring breakdown for a specific week. "
        "The caller must be an accepted member of the league.",
        tags=["Fantasy Leaderboard"],
    )
    def get_week_scores(
        self,
        fantasy_league_id: FantasyLeagueID,
        week: int,
        principal: AuthPrincipal = Depends(JWTBearer([Permissions.FANTASY_READ])),
    ) -> dict:
        return self.__leaderboard_service.get_week_scores(
            fantasy_league_id, principal.user_id, week
        )
