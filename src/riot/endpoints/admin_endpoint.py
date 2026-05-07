import logging

import httpx
from classy_fastapi import Routable, post
from fastapi import Depends

from src.auth import JWTBearer, Permissions
from src.common.config import app_config

logger = logging.getLogger("api.admin")

SCRAPER_JOBS = {
    "fetch-leagues": "/api/v1/fetch-leagues",
    "fetch-tournaments": "/api/v1/fetch-tournaments",
    "fetch-teams": "/api/v1/fetch-teams",
    "fetch-matches": "/api/v1/fetch-matches-from-schedule",
    "fetch-games": "/api/v1/fetch-games-from-matches",
    "update-game-states": "/api/v1/update-game-states",
}


class AdminEndpoint(Routable):
    @post(
        path="/trigger/{job_name}",
        description="Trigger a scraper job by name",
        tags=["Admin"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_ADMIN]))],
        status_code=202,
    )
    async def trigger_job(self, job_name: str) -> dict:
        if job_name not in SCRAPER_JOBS:
            return {"error": f"Unknown job: {job_name}. Available: {list(SCRAPER_JOBS.keys())}"}

        scraper_path = SCRAPER_JOBS[job_name]
        url = f"{app_config.SCRAPER_INTERNAL_URL}{scraper_path}"
        logger.info("Triggering scraper job=%s url=%s", job_name, url)

        async with httpx.AsyncClient() as client:
            response = await client.post(url, timeout=10)

        if response.status_code == 202:
            return {"message": f"Job '{job_name}' triggered successfully"}
        else:
            logger.error("Failed to trigger job=%s status=%s", job_name, response.status_code)
            return {"error": f"Scraper returned {response.status_code}"}

    @post(
        path="/trigger-all",
        description="Trigger all scraper jobs in sequence",
        tags=["Admin"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_ADMIN]))],
        status_code=202,
    )
    async def trigger_all_jobs(self) -> dict:
        logger.info("Triggering all scraper jobs")
        results = {}
        async with httpx.AsyncClient() as client:
            for job_name, path in SCRAPER_JOBS.items():
                url = f"{app_config.SCRAPER_INTERNAL_URL}{path}"
                try:
                    response = await client.post(url, timeout=10)
                    results[job_name] = "triggered" if response.status_code == 202 else "failed"
                except Exception as e:
                    logger.error("Failed to trigger job=%s: %s", job_name, str(e))
                    results[job_name] = f"error: {str(e)}"
        return {"results": results}
