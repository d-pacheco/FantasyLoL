import logging
import time
from typing import Callable

from fantasylol.exceptions.fantasy_lol_exception import FantasyLolException

logger = logging.getLogger('fantasy-lol')


class JobRunner:
    @staticmethod
    def run_retry_job(job_function: Callable, job_name: str, max_retries: int = 3):
        retry_count = 0
        error = None
        job_completed = False

        logger.info(f"Starting {job_name}")
        while retry_count <= max_retries and not job_completed:
            try:
                job_function()
                job_completed = True
            except FantasyLolException as e:
                retry_count += 1
                error = e
                logger.warning(f"An error occurred during {job_name}."
                               f" Retry attempt: {retry_count}")
                if retry_count <= max_retries:
                    time.sleep(5)
        if job_completed:
            logger.info(f"{job_name} completed successfully")
        else:
            logger.error(f"{job_name} failed: {error}")
