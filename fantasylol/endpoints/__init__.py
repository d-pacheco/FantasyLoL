from fastapi import APIRouter
from .riot_api import league_endpoint_v1
from .riot_api import tournament_endpoint_v1
from .riot_api import professional_team_endpoint_v1
from .riot_api import game_endpoint_v1

router = APIRouter()

# Include routes for the riot api endpoints
RIOT_ENDPOINT_PREFIX = "/riot"
router.include_router(league_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(tournament_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(professional_team_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(game_endpoint_v1.router, prefix=RIOT_ENDPOINT_PREFIX)

# Include routs for the Fantasy League of Legends api endpoints
FANTASY_ENDPOINT_PREFIX = "/fantasy-lol"
