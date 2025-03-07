import uvicorn
import sys

from src.common.logger import configure_logger
from src.db import DatabaseConnectionProvider, DatabaseService
from src.common.config import app_config
from src.riot import app
from src.riot.util.job_scheduler import JobScheduler
from src.riot.endpoints import (
    GameEndpoint,
    GameStatsEndpoint,
    JobRunnerEndpoint,
    LeagueEndpoint,
    MatchEndpoint,
    ProfessionalPlayerEndpoint,
    ProfessionalTeamEndpoint,
    TournamentEndpoint
)
from src.riot.service import (
    RiotGameService,
    RiotGameStatsService,
    RiotLeagueService,
    RiotMatchService,
    RiotProfessionalPlayerService,
    RiotProfessionalTeamService,
    RiotTournamentService
)


def main():
    configure_logger()

    # Create database service
    connection_provider = DatabaseConnectionProvider(app_config.DATABASE_URL)
    database_service = DatabaseService(connection_provider)

    # Create Riot Services
    game_service = RiotGameService(database_service)
    game_stats_service = RiotGameStatsService(database_service)
    league_service = RiotLeagueService(database_service)
    match_service = RiotMatchService(database_service)
    player_service = RiotProfessionalPlayerService(database_service)
    team_service = RiotProfessionalTeamService(database_service)
    tournament_service = RiotTournamentService(database_service)
    job_scheduler = JobScheduler(
        game_service=game_service,
        game_stats_service=game_stats_service,
        league_service=league_service,
        match_service=match_service,
        player_service=player_service,
        team_service=team_service,
        tournament_service=tournament_service
    )

    # Create endpoints
    game_endpoint = GameEndpoint(game_service)
    game_stats_endpoint = GameStatsEndpoint(game_stats_service)
    league_endpoint = LeagueEndpoint(league_service)
    match_endpoint = MatchEndpoint(match_service)
    player_endpoint = ProfessionalPlayerEndpoint(player_service)
    team_endpoint = ProfessionalTeamEndpoint(team_service)
    tournament_endpoint = TournamentEndpoint(tournament_service)
    job_runner_endpoint = JobRunnerEndpoint(job_scheduler)

    # Add endpoints to app
    app.include_router(league_endpoint.router)
    app.include_router(tournament_endpoint.router)
    app.include_router(match_endpoint.router)
    app.include_router(game_endpoint.router)
    app.include_router(game_stats_endpoint.router)
    app.include_router(team_endpoint.router)
    app.include_router(player_endpoint.router)
    app.include_router(job_runner_endpoint.router)

    job_scheduler.schedule_all_jobs()
    uvicorn.run(app, host="0.0.0.0", port=8002)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
