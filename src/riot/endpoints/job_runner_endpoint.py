from classy_fastapi import Routable, post

from src.riot.util import JobScheduler


class JobRunnerEndpoint(Routable):
    def __init__(self, job_scheduler: JobScheduler):
        super().__init__()
        self.__job_scheduler = job_scheduler

    @post(
        path="/fetch-leagues",
        description="Manually trigger fetch leagues from riot job",
        tags=["Manual Job Triggers"],
        status_code=202,
        responses={
            202: {
                "content": {
                    "application/json": {
                        "example": "Job triggered successfully"
                    }
                }
            }
        }
    )
    async def manual_fetch_leagues_from_riot_job_trigger(self) -> str:
        self.__job_scheduler.trigger_league_service_job()
        return "Job triggered successfully"

    @post(
        path="/fetch-tournaments",
        description="Manually trigger fetch tournaments from riot job",
        tags=["Manual Job Triggers"],
        status_code=202,
        responses={
            202: {
                "content": {
                    "application/json": {
                        "example": "Job triggered successfully"
                    }
                }
            }
        }
    )
    async def trigger_fetch_tournaments_from_riot_job(self) -> str:
        self.__job_scheduler.trigger_tournament_service_job()
        return "Job triggered successfully"

    @post(
        path="/fetch-matches-from-schedule",
        description="Manually trigger fetch schedule from riot job",
        tags=["Manual Job Triggers"],
        status_code=202,
        responses={
            202: {
                "content": {
                    "application/json": {
                        "example": "Job triggered successfully"
                    }
                }
            }
        }
    )
    async def trigger_fetch_schedule_from_riot_job(self) -> str:
        self.__job_scheduler.trigger_match_service_job()
        return "Job triggered successfully"

    @post(
        path="/fetch-games-from-matches",
        description="Manually trigger fetch games from match ids job",
        tags=["Manual Job Triggers"],
        status_code=202,
        responses={
            202: {
                "content": {
                    "application/json": {
                        "example": "Job triggered successfully"
                    }
                }
            }
        }
    )
    async def trigger_fetch_games_from_match_ids_job(self) -> str:
        self.__job_scheduler.trigger_games_from_match_ids_job()
        return "Job triggered successfully"

    @post(
        path="/update-game-states",
        description="Manually trigger update game states job",
        tags=["Manual Job Triggers"],
        status_code=202,
        responses={
            202: {
                "content": {
                    "application/json": {
                        "example": "Job triggered successfully"
                    }
                }
            }
        }
    )
    async def trigger_update_game_states_job(self) -> str:
        self.__job_scheduler.trigger_update_game_states_job()
        return "Job triggered successfully"

    @post(
        path="/fetch-teams",
        description="Manually trigger fetch teams from riot job",
        tags=["Manual Job Triggers"],
        status_code=202,
        responses={
            202: {
                "content": {
                    "application/json": {
                        "example": "Job triggered successfully"
                    }
                }
            }
        }
    )
    async def trigger_fetch_teams_from_riot_job(self) -> str:
        self.__job_scheduler.trigger_team_service_job()
        return "Job triggered successfully"

    @post(
        path="/fetch-players",
        description="Manually trigger fetch players from riot job",
        tags=["Manual Job Triggers"],
        status_code=202,
        responses={
            202: {
                "content": {
                    "application/json": {
                        "example": "Job triggered successfully"
                    }
                }
            }
        }
    )
    async def trigger_fetch_players_from_riot_job(self) -> str:
        self.__job_scheduler.trigger_player_service_job()
        return "Job triggered successfully"
