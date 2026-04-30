"""Lookup orchestration: ties together classification, spelling, dictionary, LLM, and storage."""

import hashlib
import sqlite3
import json

from . import classify
from . import language as lang_detect
from . import spelling
from . import morphology
from . import dictionary
from . import llm
from . import review
from .config import Config
from .models import Lookup, Entry, now_iso
from .errors import LookupError
from .classify import InputType
from .logging_config import get_logger

logger = get_logger("lookup")


def _hash_context(context: str | None) -> str | None:
    if context is None:
        return None
    return hashlib.sha256(context.encode()).hexdigest()[:16]


async def lookup(
    query: str,
    config: Config,
    conn: sqlite3.Connection,
    context: str | None = None,
    force: bool = False,
    no_save: bool = False,
    no_ai: bool = False,
    is_identifier: bool = False,
) -> dict:
    """Perform a full lookup of a word/phrase/identifier.

    This orchestrates:
    1. Classification
    2. Language detection
    3. Spelling check
    4. Morphology analysis
    5. Local dictionary lookup
    6. LLM explanation (if needed)
    7. Storage
    8. Card generation

    Returns a result dict for rendering.
    """
    # Step 1: Classify
    input_type = classify.classify(query)
    if is_identifier:
        input_type = InputType.CODE_IDENTIFIER

    logger.info("Lookup start: query=%r type=%s no_ai=%s", query, input_type, no_ai)

    # Step 2: Language detection
    language = lang_detect.detect(query)

    # Step 3: Spelling check (only for single words)
    if input_type == InputType.SINGLE_WORD:
        is_typo, suggestion, suggestions = spelling.check_spelling(query, input_type)
        if is_typo and not force:
            return {
                "query": query,
                "input_type": input_type,
                "language": language,
                "_typo": True,
                "_suggestion": suggestion,
                "_suggestions": suggestions,
                "saved": False,
            }

    # Step 4: Morphology
    morph = morphology.analyze(query)
    lemma = morph.get("lemma")

    # Step 5: Check local dictionary first
    dict_result = dictionary.lookup(query)

    context_hash = _hash_context(context)

    # Step 6: LLM explanation (default: on, use --no-ai to disable)
    llm_response = None
    llm_used = False

    should_use_llm = not no_ai and config.llm.enabled

    if should_use_llm:
        api_key = config.llm.api_key
        if api_key:
            prompt_version = llm._get_prompt_version(str(input_type))

            # Check cache
            if config.llm.cache:
                cached = llm.check_cache(conn, query, context_hash, config.llm.model, prompt_version)
                if cached:
                    llm_response = cached
                    llm_used = False  # cached, not fresh call
                    logger.info("Using cached LLM response for %r", query)

            if llm_response is None:
                logger.info("Calling LLM for %r (model=%s)", query, config.llm.model)
                llm_response = await llm.explain(
                    query=query,
                    input_type=str(input_type),
                    config=config,
                    context=context,
                    context_hash=context_hash,
                    lemma=lemma,
                    api_key=api_key,
                )
                llm_used = True

                # Save to cache
                if config.llm.cache:
                    llm.save_cache(conn, query, context_hash, config.llm.model, prompt_version, llm_response)

    # Step 7: Build result from best available source
    if llm_response:
        result = {**llm_response, "_source": "llm"}
        logger.info("Result source: llm for %r", query)
    elif dict_result:
        result = {**dict_result, "_source": "local_dict"}
        logger.info("Result source: local_dict for %r", query)
    else:
        # Minimal result from morphology + guess
        logger.info("Result source: morphology (fallback) for %r", query)
        result = {
            "query": query,
            "lemma": lemma,
            "part_of_speech": morph.get("pos", []),
            "meaning_zh": "",
            "meaning_en": "",
            "context_explanation": "",
            "technical_domain": [],
            "collocations": [],
            "examples": [],
            "common_mistakes": [],
            "cards": [],
            "_source": "morphology",
        }

    result["input_type"] = str(input_type)
    result["language"] = str(language) if language else None

    # Step 8: Save to database
    if not no_save:
        status = "forced" if force else "saved"
        if result.get("_source") == "llm" and not llm_used:
            status = "cached"

        logger.info("Saving lookup: query=%r status=%s", query, status)
        lookup_id = _save_lookup(conn, query, input_type, language, context, context_hash, status)
        entry_id = _save_entry(conn, lookup_id, result)

        # Generate cards
        card_ids = review.generate_cards_from_response(conn, entry_id, result, config)

        result["saved"] = True
        result["card_count"] = len(card_ids)
    else:
        result["saved"] = False
        result["card_count"] = 0

    return result


def _save_lookup(
    conn: sqlite3.Connection,
    query: str,
    input_type: InputType,
    language,
    context: str | None,
    context_hash: str | None,
    status: str,
) -> int:
    cursor = conn.execute(
        """INSERT INTO lookup (query, normalized_query, input_type, language, context, context_hash, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (query, query.lower(), str(input_type), str(language) if language else None,
         context, context_hash, status, now_iso()),
    )
    conn.commit()
    return cursor.lastrowid


def _save_entry(conn: sqlite3.Connection, lookup_id: int, result: dict) -> int:
    entry = Entry.from_llm_response(lookup_id, result)
    cursor = conn.execute(
        """INSERT INTO entry
           (lookup_id, lemma, part_of_speech, meaning_zh, meaning_en,
            context_explanation, technical_domain, technical_note,
            collocations, examples, common_mistakes, raw_response, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            entry.lookup_id,
            entry.lemma,
            entry.part_of_speech,
            entry.meaning_zh,
            entry.meaning_en,
            entry.context_explanation,
            entry.technical_domain,
            entry.technical_note,
            entry.collocations,
            entry.examples,
            entry.common_mistakes,
            entry.raw_response,
            entry.created_at,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_history(conn: sqlite3.Connection, limit: int = 20) -> list[dict]:
    """Get recent lookup history with associated entry data."""
    rows = conn.execute(
        """SELECT l.*, e.meaning_zh, e.technical_domain
           FROM lookup l
           LEFT JOIN entry e ON e.lookup_id = l.id
           ORDER BY l.created_at DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def get_lookup_detail(conn: sqlite3.Connection, query: str) -> dict | None:
    """Get saved details for a specific query."""
    row = conn.execute(
        """SELECT l.*, e.*
           FROM lookup l
           LEFT JOIN entry e ON e.lookup_id = l.id
           WHERE l.query = ? OR l.normalized_query = ?
           ORDER BY l.created_at DESC
           LIMIT 1""",
        (query, query.lower()),
    ).fetchone()
    return dict(row) if row else None
