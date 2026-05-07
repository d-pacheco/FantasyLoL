import logging
from contextvars import ContextVar
from pathlib import Path
from logging.handlers import RotatingFileHandler

from .config import app_config

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        rid = request_id_var.get()
        record.request_id = f"[req:{rid}] " if rid else ""  # type: ignore[attr-defined]
        return True


def configure_logger(service: str) -> None:
    max_file_size = 1024 * 1024 * 100  # 100 MB
    backup_count = 5

    logging_level = logging.DEBUG if app_config.DEBUG_LOGGING else logging.INFO

    root_logger = logging.getLogger(service)
    root_logger.setLevel(logging_level)

    # Avoid duplicate handlers on re-init
    if root_logger.handlers:
        return

    rid_filter = RequestIdFilter()

    # Console handler
    console_fmt = logging.Formatter(
        "[%(levelname)s] %(asctime)s [%(name)s] %(request_id)s%(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(console_fmt)
    console_handler.addFilter(rid_filter)
    root_logger.addHandler(console_handler)

    # File handler
    if app_config.FILE_LOGGING_ENABLED:
        Path("./logs/").mkdir(parents=True, exist_ok=True)
        file_fmt = logging.Formatter(
            "[%(levelname)s] %(asctime)s [%(name)s] %(request_id)s%(message)s"
        )
        file_handler = RotatingFileHandler(
            filename=f"./logs/{service}.log",
            mode="a+",
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging_level)
        file_handler.setFormatter(file_fmt)
        file_handler.addFilter(rid_filter)
        root_logger.addHandler(file_handler)

    # Loki handler
    if app_config.LOKI_ENABLED:
        try:
            import logging_loki  # type: ignore[import-untyped,import-not-found]

            loki_handler = logging_loki.LokiHandler(
                url=app_config.LOKI_URL,
                tags={"app": "mythicforge", "service": service},
                version="1",
            )
            loki_fmt = logging.Formatter("[%(levelname)s] %(request_id)s%(message)s")
            loki_handler.setFormatter(loki_fmt)
            loki_handler.addFilter(rid_filter)
            loki_handler.setLevel(logging_level)
            root_logger.addHandler(loki_handler)
        except ImportError:
            root_logger.warning("python-logging-loki not installed, Loki logging disabled")
