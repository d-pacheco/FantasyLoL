from fastapi import APIRouter
from . import fantasy_league_endpoint_v1, user_endpoint_v1

router = APIRouter()

FANTASY_ENDPOINT_PREFIX = "/fantasy"
router.include_router(user_endpoint_v1.router, prefix=FANTASY_ENDPOINT_PREFIX)
router.include_router(fantasy_league_endpoint_v1.router, prefix=FANTASY_ENDPOINT_PREFIX)
