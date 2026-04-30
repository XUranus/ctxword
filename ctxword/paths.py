import os
from pathlib import Path


def _root() -> Path:
    base = os.environ.get("CTXWORD_DATA", "~/.local/share/ctxword")
    return Path(os.path.expanduser(base)).resolve()


def get_data_dir() -> Path:
    return _root()


def get_logs_dir() -> Path:
    return _root() / "logs"


def get_llm_dir() -> Path:
    return _root() / "llm"


def get_database_path() -> Path:
    return _root() / "ctxword.db"


def ensure_dirs() -> None:
    _root().mkdir(parents=True, exist_ok=True)
    get_logs_dir().mkdir(parents=True, exist_ok=True)
    get_llm_dir().mkdir(parents=True, exist_ok=True)
