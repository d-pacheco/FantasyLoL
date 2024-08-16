from fastapi import APIRouter
from . import (
    game_endpoint_v1,
    game_stats_endpoint,
    league_endpoint_v1,
    match_endpoint_v1,
    professional_player_endpoint_v1,
    professional_team_endpoint_v1,
    tournament_endpoint_v1,
    #job_runner_endpoint
)

router = APIRouter()

RIOT_ENDPOINT_PREFIX = "/riot"
router.include_router(league_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(tournament_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(match_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(game_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(game_stats_endpoint.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(professional_team_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(professional_player_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)

#router.include_router(job_runner_endpoint.router)
