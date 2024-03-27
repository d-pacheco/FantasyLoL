import uvicorn
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from src.riot import app
from src.common.config import Config
from src.riot.util.job_scheduler import JobScheduler


def configure_logger():
    max_file_size = 1024 * 1024 * 100  # 100 MB
    backup_count = 5  # keep up to 5 files
    Path("./logs/").mkdir(parents=True, exist_ok=True)
    if Config.DEBUG_LOGGING:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    fantasy_lol_logger = logging.getLogger('fantasy-lol')
    fantasy_lol_logger.setLevel(logging_level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

    # File handler
    file_handler = RotatingFileHandler(
        filename="./logs/fantasylol.log",
        mode="a+",
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(formatter)
    fantasy_lol_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(formatter)
    fantasy_lol_logger.addHandler(console_handler)


if __name__ == "__main__":
    configure_logger()
    job_scheduler = JobScheduler()
    job_scheduler.schedule_all_jobs()
    uvicorn.run(app, host="0.0.0.0", port=80)
