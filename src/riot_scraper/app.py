import uvicorn
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination.utils import disable_installed_extensions_check

from src.common.logger import configure_logger
from src.common.config import app_config
from src.db import DatabaseConnectionProvider, DatabaseService
from src.riot_scraper.job_runner import JobRunner
from src.riot_scraper.riot_api.api_requester import ApiRequester
from src.riot_scraper.riot_api.riot_api_client import RiotApiClient
from src.riot_scraper.scrapers import (
    RiotGameScraper,
    RiotGameStatsScraper,
    RiotLeagueScraper,
    RiotMatchScraper,
    RiotTeamScraper,
    RiotTournamentScraper,
)
from src.riot_scraper.job_scheduler import JobScheduler
from src.riot_scraper.job_runner_endpoint import JobRunnerEndpoint


def get_bool_env(var_name, default=False):
    value = os.getenv(var_name)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def configure_job_schedule(db_service: DatabaseService) -> JobScheduler:
    api_requester = ApiRequester()
    riot_api_client = RiotApiClient(api_requester)
    job_runner = JobRunner()
    game_scraper = RiotGameScraper(db_service, riot_api_client, job_runner)
    game_stats_scraper = RiotGameStatsScraper(db_service, riot_api_client, job_runner)
    league_scraper = RiotLeagueScraper(db_service, riot_api_client, job_runner)
    match_scraper = RiotMatchScraper(db_service, riot_api_client, job_runner)
    team_scraper = RiotTeamScraper(db_service, riot_api_client, job_runner)
    tournament_scraper = RiotTournamentScraper(db_service, riot_api_client, job_runner)

    job_scheduler = JobScheduler(
        game_service=game_scraper,
        game_stats_service=game_stats_scraper,
        league_service=league_scraper,
        match_service=match_scraper,
        team_service=team_scraper,
        tournament_service=tournament_scraper,
    )
    return job_scheduler


def configure_api_endpoints(job_runner_endpoint: JobRunnerEndpoint) -> FastAPI:
    app = FastAPI(
        title="MythicForge Riot Job Schedule API",
        version="0.1.0",
        description="""
            Fetch data related to Professional League of Legends.
            Requires admin permissions to trigger jobs
            """,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    disable_installed_extensions_check()
    app.include_router(job_runner_endpoint.router, prefix="/api/v1")

    return app


def main():
    configure_logger("scraper")

    connection_provider = DatabaseConnectionProvider(app_config.DATABASE_URL)
    database_service = DatabaseService(connection_provider)

    is_master_node = get_bool_env("MASTER_SCRAPER")
    if is_master_node:
        job_scheduler = configure_job_schedule(database_service)
        job_runner_endpoint = JobRunnerEndpoint(job_scheduler)
        app = configure_api_endpoints(job_runner_endpoint)

        job_scheduler.schedule_all_jobs()
        uvicorn.run(app, host="0.0.0.0", port=8004)

    else:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
