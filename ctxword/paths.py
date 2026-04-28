import os
from pathlib import Path


def _expand(path: str) -> Path:
    return Path(os.path.expanduser(path)).resolve()


def get_data_dir() -> Path:
    base = os.environ.get("CTXWORD_DATA_DIR", "~/.local/share/ctxword")
    return _expand(base)


def get_config_dir() -> Path:
    base = os.environ.get("CTXWORD_CONFIG_DIR", "~/.config/ctxword")
    return _expand(base)


def get_cache_dir() -> Path:
    base = os.environ.get("CTXWORD_CACHE_DIR", "~/.cache/ctxword")
    return _expand(base)


def get_database_path() -> Path:
    return get_data_dir() / "ctxword.db"


def get_config_path() -> Path:
    return get_config_dir() / "config.toml"


def ensure_dirs() -> None:
    get_data_dir().mkdir(parents=True, exist_ok=True)
    get_config_dir().mkdir(parents=True, exist_ok=True)
    get_cache_dir().mkdir(parents=True, exist_ok=True)
