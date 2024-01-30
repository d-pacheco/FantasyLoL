from fastapi import APIRouter
from .riot_api import (
    league_endpoint_v1,
    tournament_endpoint_v1,
    game_stats_endpoint,
    professional_player_endpoint_v1,
    professional_team_endpoint_v1,
    game_endpoint_v1,
    match_endpoint_v1
)
from .fantasy_api import (
    user_endpoint_v1,
    fantasy_league_endpoint_v1
)
from . import job_runner_endpoint

router = APIRouter()

# Include routes for the riot api endpoints
RIOT_ENDPOINT_PREFIX = "/riot"
router.include_router(league_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(tournament_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(match_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(game_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(game_stats_endpoint.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(professional_team_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(professional_player_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)


router.include_router(job_runner_endpoint.router)


# Include routs for the Fantasy League of Legends api endpoints
FANTASY_ENDPOINT_PREFIX = "/fantasy"
router.include_router(user_endpoint_v1.router, prefix=FANTASY_ENDPOINT_PREFIX)
router.include_router(fantasy_league_endpoint_v1.router, prefix=FANTASY_ENDPOINT_PREFIX)
