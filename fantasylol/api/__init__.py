from fastapi import APIRouter
from .riot_api import LeagueEndpointV1
from .riot_api import TournamentEndpointV1
from .riot_api import ProfessionalTeamEndpointV1

router = APIRouter()

# Include routes for the riot api endpoints
RIOT_ENDPOINT_PREFIX = "/riot"
router.include_router(LeagueEndpointV1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(TournamentEndpointV1.router, prefix=RIOT_ENDPOINT_PREFIX)
router.include_router(ProfessionalTeamEndpointV1.router, prefix=RIOT_ENDPOINT_PREFIX)

# Include routs for the Fantasy League of Legends api endpoints
FANTASY_ENDPOINT_PREFIX = "/fantasy-lol"
