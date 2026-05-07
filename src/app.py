import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from src.common.config import app_config
from src.common.logger import configure_logger
from src.common.middleware import RequestLoggingMiddleware
from src.db.database_connection_provider import DatabaseConnectionProvider
from src.db.database_service import DatabaseService
from src.fantasy.endpoints import FantasyLeagueEndpoint, FantasyTeamEndpoint, UserEndpointV1
from src.fantasy.service import FantasyLeagueService, FantasyTeamService, UserService
from src.riot.endpoints import (
    GameEndpoint,
    GameStatsEndpoint,
    LeagueEndpoint,
    MatchEndpoint,
    ProfessionalPlayerEndpoint,
    ProfessionalTeamEndpoint,
    TournamentEndpoint,
)
from src.riot.service import (
    RiotGameService,
    RiotGameStatsService,
    RiotLeagueService,
    RiotMatchService,
    RiotProfessionalPlayerService,
    RiotProfessionalTeamService,
    RiotTournamentService,
)


def create_app(database_service: DatabaseService) -> FastAPI:
    app = FastAPI(
        title="MythicForge API",
        version="0.1.0",
        description="Fantasy League of Legends platform with Professional LoL data.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    disable_installed_extensions_check()

    # Riot services and endpoints
    game_service = RiotGameService(database_service)
    game_stats_service = RiotGameStatsService(database_service)
    league_service = RiotLeagueService(database_service)
    match_service = RiotMatchService(database_service)
    player_service = RiotProfessionalPlayerService(database_service)
    team_service = RiotProfessionalTeamService(database_service)
    tournament_service = RiotTournamentService(database_service)

    app.include_router(LeagueEndpoint(league_service).router, prefix="/api/v1/riot")
    app.include_router(TournamentEndpoint(tournament_service).router, prefix="/api/v1/riot")
    app.include_router(MatchEndpoint(match_service).router, prefix="/api/v1/riot")
    app.include_router(GameEndpoint(game_service).router, prefix="/api/v1/riot")
    app.include_router(GameStatsEndpoint(game_stats_service).router, prefix="/api/v1/riot")
    app.include_router(ProfessionalTeamEndpoint(team_service).router, prefix="/api/v1/riot")
    app.include_router(ProfessionalPlayerEndpoint(player_service).router, prefix="/api/v1/riot")

    # Fantasy services and endpoints
    user_service = UserService(database_service)
    fantasy_league_service = FantasyLeagueService(database_service)
    fantasy_team_service = FantasyTeamService(database_service)

    app.include_router(UserEndpointV1(user_service).router, prefix="/api/v1")
    app.include_router(
        FantasyLeagueEndpoint(fantasy_league_service).router, prefix="/api/v1/fantasy"
    )
    app.include_router(FantasyTeamEndpoint(fantasy_team_service).router, prefix="/api/v1/fantasy")

    add_pagination(app)

    return app


def main():
    configure_logger("api")

    connection_provider = DatabaseConnectionProvider(app_config.DATABASE_URL)
    database_service = DatabaseService(connection_provider)

    application = create_app(database_service)
    uvicorn.run(application, host="0.0.0.0", port=8002)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
