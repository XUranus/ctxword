"""Database initialization and connection management."""

import sqlite3
from pathlib import Path

from . import paths
from .errors import DatabaseError


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    if db_path is None:
        paths.ensure_dirs()
        db_path = paths.get_database_path()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    from .migrations import run_migrations
    run_migrations(conn)
