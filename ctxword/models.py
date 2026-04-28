from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Lookup:
    id: int | None = None
    query: str = ""
    normalized_query: str | None = None
    input_type: str = "unknown"
    language: str | None = None
    context: str | None = None
    context_hash: str | None = None
    source: str | None = None
    status: str = "saved"
    created_at: str = field(default_factory=now_iso)


@dataclass
class Entry:
    id: int | None = None
    lookup_id: int = 0
    lemma: str | None = None
    part_of_speech: str | None = None
    meaning_zh: str | None = None
    meaning_en: str | None = None
    context_explanation: str | None = None
    technical_domain: str | None = None
    technical_note: str | None = None
    collocations: str | None = None
    examples: str | None = None
    common_mistakes: str | None = None
    raw_response: str | None = None
    created_at: str = field(default_factory=now_iso)

    @classmethod
    def from_llm_response(cls, lookup_id: int, response: dict[str, Any]) -> Entry:
        def _to_json(val):
            if val is None:
                return None
            return json.dumps(val, ensure_ascii=False)

        return cls(
            lookup_id=lookup_id,
            lemma=response.get("lemma"),
            part_of_speech=_to_json(response.get("part_of_speech")),
            meaning_zh=response.get("meaning_zh"),
            meaning_en=response.get("meaning_en"),
            context_explanation=response.get("context_explanation"),
            technical_domain=_to_json(response.get("technical_domain")),
            technical_note=response.get("technical_note"),
            collocations=_to_json(response.get("collocations")),
            examples=_to_json(response.get("examples")),
            common_mistakes=_to_json(response.get("common_mistakes")),
            raw_response=json.dumps(response, ensure_ascii=False),
        )


@dataclass
class ReviewCard:
    id: int | None = None
    entry_id: int = 0
    card_type: str = "meaning"
    front: str = ""
    back: str = ""
    tags: str | None = None
    due_at: str | None = None
    interval_days: float = 0.0
    ease: float = 2.5
    reps: int = 0
    lapses: int = 0
    state: str = "new"
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)


@dataclass
class ReviewLog:
    id: int | None = None
    card_id: int = 0
    rating: str = ""
    reviewed_at: str = field(default_factory=now_iso)
    elapsed_ms: int | None = None
    old_due_at: str | None = None
    new_due_at: str | None = None
    old_interval_days: float | None = None
    new_interval_days: float | None = None


@dataclass
class LLMCache:
    id: int | None = None
    cache_key: str = ""
    query: str = ""
    context_hash: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    response_json: str = ""
    created_at: str = field(default_factory=now_iso)
