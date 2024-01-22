import logging
from fastapi import APIRouter

from fantasylol.util.job_scheduler import JobScheduler

VERSION = "v1"
router = APIRouter(prefix=f"/jobs/{VERSION}")
job_scheduler = JobScheduler()
logger = logging.getLogger('fantasy-lol')


@router.post(
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
async def manual_fetch_leagues_from_riot_job_trigger():
    job_scheduler.trigger_league_service_job()
    return "Job triggered successfully"


@router.post(
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
async def trigger_update_game_states_job():
    job_scheduler.trigger_update_game_states_job()
    return "Job triggered successfully"


@router.post(
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
async def trigger_fetch_games_from_match_ids_job():
    job_scheduler.trigger_games_from_match_ids_job()
    return "Job triggered successfully"
