"""Database migrations."""

import sqlite3

MIGRATIONS = [
    # Version 1: Initial schema
    """
    CREATE TABLE IF NOT EXISTS lookup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        normalized_query TEXT,
        input_type TEXT NOT NULL DEFAULT 'unknown',
        language TEXT,
        context TEXT,
        context_hash TEXT,
        source TEXT,
        status TEXT NOT NULL DEFAULT 'saved',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS entry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lookup_id INTEGER NOT NULL,
        lemma TEXT,
        part_of_speech TEXT,
        meaning_zh TEXT,
        meaning_en TEXT,
        context_explanation TEXT,
        technical_domain TEXT,
        technical_note TEXT,
        collocations TEXT,
        examples TEXT,
        common_mistakes TEXT,
        raw_response TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (lookup_id) REFERENCES lookup(id)
    );

    CREATE TABLE IF NOT EXISTS review_card (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id INTEGER NOT NULL,
        card_type TEXT NOT NULL DEFAULT 'meaning',
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        tags TEXT,
        due_at TEXT,
        interval_days REAL DEFAULT 0,
        ease REAL DEFAULT 2.5,
        reps INTEGER DEFAULT 0,
        lapses INTEGER DEFAULT 0,
        state TEXT DEFAULT 'new',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (entry_id) REFERENCES entry(id)
    );

    CREATE TABLE IF NOT EXISTS review_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        rating TEXT NOT NULL,
        reviewed_at TEXT NOT NULL,
        elapsed_ms INTEGER,
        old_due_at TEXT,
        new_due_at TEXT,
        old_interval_days REAL,
        new_interval_days REAL,
        FOREIGN KEY (card_id) REFERENCES review_card(id)
    );

    CREATE TABLE IF NOT EXISTS llm_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cache_key TEXT NOT NULL UNIQUE,
        query TEXT NOT NULL,
        context_hash TEXT,
        model TEXT,
        prompt_version TEXT,
        response_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY
    );
    """,
]

SCHEMA_VERSION = len(MIGRATIONS)


def get_current_version(conn: sqlite3.Connection) -> int:
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)")
    row = conn.execute("SELECT MAX(version) as v FROM schema_version").fetchone()
    return row["v"] if row["v"] is not None else 0


def run_migrations(conn: sqlite3.Connection) -> None:
    current = get_current_version(conn)

    for i, migration in enumerate(MIGRATIONS[current:], start=current + 1):
        conn.executescript(migration)
        conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (?)", (i,))

    conn.commit()
