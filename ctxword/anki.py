"""Anki export: TSV/CSV export for Anki import."""

import csv
import io
import sqlite3
from pathlib import Path

from .errors import ExportError


def export_tsv(
    conn: sqlite3.Connection,
    output_path: str | Path,
    tag_filter: str | None = None,
) -> int:
    """Export review cards as TSV for Anki import.

    Columns: front, back, tags, source_context

    Returns the number of cards exported.
    """
    output_path = Path(output_path)

    query = """SELECT rc.front, rc.back, rc.tags,
                      e.context_explanation, e.meaning_zh, e.meaning_en
               FROM review_card rc
               JOIN entry e ON rc.entry_id = e.id
               ORDER BY rc.id"""

    rows = conn.execute(query).fetchall()

    if not rows:
        raise ExportError("No cards to export.")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["front", "back", "tags", "context"])
        for row in rows:
            writer.writerow([
                row["front"],
                row["back"],
                row["tags"] or "",
                row["context_explanation"] or row["meaning_en"] or "",
            ])

    return len(rows)


def export_csv(
    conn: sqlite3.Connection,
    output_path: str | Path,
    tag_filter: str | None = None,
) -> int:
    """Export review cards as CSV for Anki import.

    Returns the number of cards exported.
    """
    output_path = Path(output_path)

    query = """SELECT rc.front, rc.back, rc.tags,
                      e.context_explanation, e.meaning_zh, e.meaning_en
               FROM review_card rc
               JOIN entry e ON rc.entry_id = e.id
               ORDER BY rc.id"""

    rows = conn.execute(query).fetchall()

    if not rows:
        raise ExportError("No cards to export.")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["front", "back", "tags", "context"])
        for row in rows:
            writer.writerow([
                row["front"],
                row["back"],
                row["tags"] or "",
                row["context_explanation"] or row["meaning_en"] or "",
            ])

    return len(rows)
