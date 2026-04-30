"""Review system: card scheduling and review session management."""

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

from .config import Config
from .models import ReviewCard, ReviewLog, now_iso
from .logging_config import get_logger

logger = get_logger("review")


# SM-2 like simple scheduler
INTERVALS = {
    "new": {
        "again": timedelta(minutes=10),
        "hard": timedelta(days=1),
        "good": timedelta(days=3),
        "easy": timedelta(days=7),
    },
    "learning": {
        "again": timedelta(minutes=10),
        "hard": timedelta(days=1),
        "good": timedelta(days=3),
        "easy": timedelta(days=7),
    },
    "review": {
        "again": timedelta(days=1),
        "hard": 1.2,    # multiplier
        "good": 2.5,    # multiplier
        "easy": 3.5,    # multiplier
    },
}

EASE_ADJUST = {
    "again": -0.20,
    "hard": -0.15,
    "good": 0.0,
    "easy": 0.15,
}

MIN_EASE = 1.3


def _compute_next(
    state: str,
    interval_days: float,
    ease: float,
    rating: str,
) -> tuple[str, float, float, str]:
    """Compute next review state, interval, ease, and due date.

    Returns (new_state, new_interval_days, new_ease, due_at_iso).
    """
    new_ease = max(MIN_EASE, ease + EASE_ADJUST.get(rating, 0))

    if state in ("new", "learning"):
        delta = INTERVALS["new"].get(rating, timedelta(days=1))
        new_interval = delta.total_seconds() / 86400  # convert to days
        if rating == "again":
            new_state = "learning"
        else:
            new_state = "learning" if state == "new" else "learning"
            if rating in ("good", "easy"):
                new_state = "review"
    else:
        # Review state: multiply interval
        multiplier = INTERVALS["review"].get(rating, 2.5)
        if isinstance(multiplier, (int, float)):
            if rating == "again":
                new_interval = timedelta(days=1).total_seconds() / 86400
                new_state = "learning"
            else:
                new_interval = interval_days * multiplier
                new_state = "review"
        else:
            new_interval = multiplier.total_seconds() / 86400
            new_state = "learning"

    due_at = datetime.now(timezone.utc) + timedelta(days=new_interval)
    return new_state, new_interval, new_ease, due_at.isoformat()


def generate_cards_from_response(conn: sqlite3.Connection, entry_id: int, response: dict, config: Config) -> list[int]:
    """Generate review cards from an LLM response.

    Returns list of created card IDs.
    """
    max_cards = config.general.max_cards_per_lookup
    card_ids: list[int] = []

    # Use cards from LLM response if available
    llm_cards = response.get("cards", [])
    for card_data in llm_cards[:max_cards]:
        card_id = _insert_card(conn, entry_id, card_data)
        card_ids.append(card_id)

    # Generate basic meaning card if no cards from LLM
    if not card_ids and response.get("meaning_zh"):
        card_data = {
            "type": "meaning",
            "front": f'What does "{response.get("query", "")}" mean?',
            "back": response.get("meaning_zh", ""),
            "tags": response.get("technical_domain", []),
        }
        card_id = _insert_card(conn, entry_id, card_data)
        card_ids.append(card_id)

    logger.info("Generated %d cards for entry %d", len(card_ids), entry_id)
    return card_ids


def _insert_card(conn: sqlite3.Connection, entry_id: int, card_data: dict) -> int:
    """Insert a single review card."""
    import json as _json

    tags = card_data.get("tags", [])
    tags_str = _json.dumps(tags, ensure_ascii=False) if isinstance(tags, list) else str(tags)

    now = now_iso()

    cursor = conn.execute(
        """INSERT INTO review_card
           (entry_id, card_type, front, back, tags, due_at, interval_days, ease, reps, lapses, state, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            entry_id,
            card_data.get("type", "meaning"),
            card_data.get("front", ""),
            card_data.get("back", ""),
            tags_str,
            now,  # due immediately for new cards
            0,
            2.5,
            0,
            0,
            "new",
            now,
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_due_cards(conn: sqlite3.Connection, config: Config, limit: int | None = None) -> list[dict[str, Any]]:
    """Get cards due for review."""
    if limit is None:
        limit = config.review.review_cards_per_day

    now = now_iso()
    rows = conn.execute(
        """SELECT rc.*, e.meaning_zh, e.meaning_en
           FROM review_card rc
           JOIN entry e ON rc.entry_id = e.id
           WHERE rc.due_at <= ?
           ORDER BY rc.state = 'new' DESC, rc.due_at ASC
           LIMIT ?""",
        (now, limit),
    ).fetchall()

    return [dict(row) for row in rows]


def rate_card(
    conn: sqlite3.Connection,
    card_id: int,
    rating: str,
    elapsed_ms: int | None = None,
) -> dict:
    """Rate a review card and update its scheduling.

    Returns updated card info dict.
    """
    card_row = conn.execute(
        "SELECT * FROM review_card WHERE id = ?", (card_id,)
    ).fetchone()

    if not card_row:
        raise ValueError(f"Card {card_id} not found")

    card = dict(card_row)
    old_state = card["state"]
    old_interval = card["interval_days"] or 0
    old_ease = card["ease"] or 2.5
    old_due = card["due_at"]

    new_state, new_interval, new_ease, new_due = _compute_next(
        old_state, old_interval, old_ease, rating
    )

    new_reps = card["reps"] + 1
    new_lapses = card["lapses"] + (1 if rating == "again" else 0)

    now = now_iso()

    conn.execute(
        """UPDATE review_card
           SET state = ?, interval_days = ?, ease = ?, reps = ?, lapses = ?,
               due_at = ?, updated_at = ?
           WHERE id = ?""",
        (new_state, new_interval, new_ease, new_reps, new_lapses, new_due, now, card_id),
    )

    # Record review log
    conn.execute(
        """INSERT INTO review_log
           (card_id, rating, reviewed_at, elapsed_ms, old_due_at, new_due_at,
            old_interval_days, new_interval_days)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            card_id,
            rating,
            now,
            elapsed_ms,
            old_due,
            new_due,
            old_interval,
            new_interval,
        ),
    )

    conn.commit()

    logger.info("Card %d rated: %s state=%s→%s interval=%.1fd",
                card_id, rating, old_state, new_state, new_interval)

    return {
        "card_id": card_id,
        "rating": rating,
        "new_state": new_state,
        "new_interval_days": new_interval,
        "new_due_at": new_due,
    }


def get_stats(conn: sqlite3.Connection) -> dict[str, Any]:
    """Get learning statistics."""
    now = now_iso()
    today = now[:10]

    total_lookups = conn.execute("SELECT COUNT(*) as c FROM lookup").fetchone()["c"]
    total_cards = conn.execute("SELECT COUNT(*) as c FROM review_card").fetchone()["c"]
    due_cards = conn.execute(
        "SELECT COUNT(*) as c FROM review_card WHERE due_at <= ?", (now,)
    ).fetchone()["c"]
    new_cards = conn.execute(
        "SELECT COUNT(*) as c FROM review_card WHERE state = 'new'"
    ).fetchone()["c"]
    learning_cards = conn.execute(
        "SELECT COUNT(*) as c FROM review_card WHERE state = 'learning'"
    ).fetchone()["c"]
    mature_cards = conn.execute(
        "SELECT COUNT(*) as c FROM review_card WHERE state = 'review' AND reps >= 3"
    ).fetchone()["c"]
    reviews_today = conn.execute(
        "SELECT COUNT(*) as c FROM review_log WHERE reviewed_at >= ?", (today,)
    ).fetchone()["c"]

    # Cache hit rate
    total_llm_calls = conn.execute(
        "SELECT COUNT(*) as c FROM llm_cache"
    ).fetchone()["c"]
    total_lookups_with_ai = conn.execute(
        "SELECT COUNT(*) as c FROM lookup WHERE status != 'not_saved'"
    ).fetchone()["c"]

    cache_hit_rate = 0.0
    if total_lookups_with_ai > 0:
        cache_hit_rate = (total_lookups_with_ai - total_llm_calls) / max(total_lookups_with_ai, 1)

    return {
        "total_lookups": total_lookups,
        "total_cards": total_cards,
        "due_cards": due_cards,
        "new_cards": new_cards,
        "learning_cards": learning_cards,
        "mature_cards": mature_cards,
        "reviews_today": reviews_today,
        "cache_hit_rate": max(0, min(1, cache_hit_rate)),
    }
