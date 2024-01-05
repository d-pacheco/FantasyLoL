import uvicorn
import logging
from pathlib import Path

from fantasylol import app
from fantasylol.util.config import Config
from fantasylol.util.job_scheduler import JobScheduler


if __name__ == "__main__":
    Path("./logs/").mkdir(parents=True, exist_ok=True)
    if Config.DEBUG_LOGGING:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    logging.basicConfig(
        filename="./logs/fantasylol.log",
        filemode="a+",
        level=logging_level,
        format="%(asctime)s %(levelname)s: %(message)s",
        encoding='utf-8'
    )
    job_scheduler = JobScheduler()
    job_scheduler.schedule_all_jobs()
    uvicorn.run(app, host="0.0.0.0", port=80)
