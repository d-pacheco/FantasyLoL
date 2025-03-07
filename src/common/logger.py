import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from .config import app_config  # type: ignore


def configure_logger(logger_name: str):
    max_file_size = 1024 * 1024 * 100  # 100 MB
    backup_count = 5  # keep up to 5 files
    Path("./logs/").mkdir(parents=True, exist_ok=True)
    if app_config.DEBUG_LOGGING:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    fantasy_lol_logger = logging.getLogger(logger_name)
    fantasy_lol_logger.setLevel(logging_level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

    # File handler
    file_handler = RotatingFileHandler(
        filename=f"./logs/{logger_name}.log",
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
