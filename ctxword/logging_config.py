"""Logging setup: file-based logging to CTXWORD_DATA/logs/."""

import logging
from pathlib import Path

from .paths import get_logs_dir

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_log_initialized = False


def init_logging(level: int = logging.INFO) -> None:
    """Configure file-based logging. Idempotent — only runs once."""
    global _log_initialized
    if _log_initialized:
        return

    logs_dir = get_logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(
        logs_dir / "ctxword.log", encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

    root = logging.getLogger("ctxword")
    root.setLevel(level)
    root.addHandler(handler)

    _log_initialized = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module under the 'ctxword' namespace."""
    return logging.getLogger(f"ctxword.{name}")
