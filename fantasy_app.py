import uvicorn
import sys
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from src.db.database_connection_provider import DatabaseConnectionProvider
from src.db.database_service import DatabaseService
from src.fantasy.service import (
    FantasyLeagueService,
    FantasyTeamService,
    UserService
)
from src.fantasy.endpoints import (
    FantasyLeagueEndpoint,
    FantasyTeamEndpoint,
    UserEndpointV1
)
from src.common.logger import configure_logger


def main():
    app = FastAPI()
    add_pagination(app)
    disable_installed_extensions_check()

    connection_provider = DatabaseConnectionProvider("sqlite:///./database/fantasy-league-of-legends.db")
    db_service = DatabaseService(connection_provider)

    fantasy_league_service = FantasyLeagueService(db_service)
    fantasy_league_endpoint = FantasyLeagueEndpoint(fantasy_league_service)

    fantasy_team_service = FantasyTeamService(db_service)
    fantasy_team_endpoint = FantasyTeamEndpoint(fantasy_team_service)

    user_service = UserService(db_service)
    user_endpoint_v1 = UserEndpointV1(user_service)

    app.include_router(fantasy_league_endpoint.router)
    app.include_router(fantasy_team_endpoint.router)
    app.include_router(user_endpoint_v1.router)

    try:
        configure_logger()
        uvicorn.run(app, host="0.0.0.0", port=80)
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
