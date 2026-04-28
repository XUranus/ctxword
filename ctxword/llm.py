"""LLM client for OpenAI-compatible APIs."""

import json
import hashlib
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from .config import Config
from .errors import LLMError

# Prompt versions for cache tracking
PROMPT_VERSION_EXPLAIN_WORD = "explain_word_v1"
PROMPT_VERSION_EXPLAIN_PHRASE = "explain_phrase_v1"
PROMPT_VERSION_EXPLAIN_IDENTIFIER = "explain_identifier_v1"

SYSTEM_PROMPT = """You are an English learning assistant for Chinese-speaking programmers.
Your job is to explain English words, phrases, and code identifiers in technical context.
Do not only translate. Explain the actual meaning in the given context.
Prefer concise, accurate, programmer-friendly explanations.
Return valid JSON only, without markdown formatting or code blocks."""


class LLMResponse(BaseModel):
    query: str
    normalized_query: str = ""
    input_type: str = "unknown"
    lemma: str = ""
    part_of_speech: list[str] = []
    meaning_zh: str = ""
    meaning_en: str = ""
    context_explanation: str = ""
    technical_domain: list[str] = []
    technical_note: str = ""
    collocations: list[str] = []
    examples: list[dict] = []
    common_mistakes: list[str] = []
    cards: list[dict] = []


def _build_user_prompt(
    query: str,
    input_type: str,
    context: str | None = None,
    lemma: str | None = None,
) -> str:
    parts: list[str] = [
        f"Target: {query}",
        f"Input type: {input_type}",
    ]
    if context:
        parts.append(f"Context: {context}")
    if lemma:
        parts.append(f"Lemma (base form): {lemma}")
    parts.extend([
        "User language: Chinese",
        "",
        "Please analyze the target item and return JSON with:",
        "- normalized_query: the base/normalized form",
        "- lemma: the dictionary form of the word",
        "- part_of_speech: list of parts of speech",
        "- meaning_zh: Chinese meaning",
        "- meaning_en: English meaning",
        "- context_explanation: explanation specific to the given context (if any)",
        "- technical_domain: list of technical domains if applicable",
        "- technical_note: programming-specific notes if applicable",
        "- collocations: common word combinations",
        "- examples: list of dicts with en and zh keys",
        "- common_mistakes: list of common errors to avoid",
        "- cards: list of dicts with type, front, back, tags fields (max 3 cards)",
    ])

    return "\n".join(parts)


def _get_prompt_version(input_type: str) -> str:
    if input_type == "code_identifier":
        return PROMPT_VERSION_EXPLAIN_IDENTIFIER
    if input_type == "phrase":
        return PROMPT_VERSION_EXPLAIN_PHRASE
    return PROMPT_VERSION_EXPLAIN_WORD


def _make_cache_key(query: str, context_hash: str | None, model: str, prompt_version: str) -> str:
    raw = f"{query}|{context_hash or ''}|{model}|{prompt_version}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def explain(
    query: str,
    input_type: str,
    config: Config,
    context: str | None = None,
    context_hash: str | None = None,
    lemma: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Call the LLM to explain a word/phrase/identifier.

    Returns a validated dict matching the LLMResponse schema.
    """
    if not config.llm.enabled:
        raise LLMError("LLM is disabled in config. Use --ai to override.")

    if api_key is None:
        raise LLMError(
            f"API key not found. Set the {config.llm.api_key_env} environment variable "
            f"or configure llm.api_key_env in {config.llm.api_key_env}."
        )

    prompt_version = _get_prompt_version(input_type)
    user_prompt = _build_user_prompt(query, input_type, context, lemma)

    payload = {
        "model": config.llm.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": config.llm.temperature,
        "max_tokens": config.llm.max_tokens,
    }

    url = f"{config.llm.base_url.rstrip('/')}/chat/completions"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise LLMError(f"LLM API error: {e.response.status_code} {e.response.text[:200]}")
        except httpx.RequestError as e:
            raise LLMError(f"LLM API request failed: {e}")

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    # Try to parse JSON from content (strip potential markdown code blocks)
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        raise LLMError(f"Failed to parse LLM response as JSON: {e}\nRaw: {content[:500]}")

    try:
        validated = LLMResponse.model_validate(parsed)
    except ValidationError as e:
        raise LLMError(f"LLM response missing required fields: {e}")

    return validated.model_dump()


def check_cache(
    conn,
    query: str,
    context_hash: str | None,
    model: str,
    prompt_version: str,
) -> dict | None:
    """Check if a cached LLM result exists."""
    cache_key = _make_cache_key(query, context_hash, model, prompt_version)
    row = conn.execute(
        "SELECT response_json FROM llm_cache WHERE cache_key = ?", (cache_key,)
    ).fetchone()
    if row:
        try:
            return json.loads(row["response_json"])
        except json.JSONDecodeError:
            return None
    return None


def save_cache(
    conn,
    query: str,
    context_hash: str | None,
    model: str,
    prompt_version: str,
    response: dict,
) -> None:
    """Save an LLM result to the cache."""
    cache_key = _make_cache_key(query, context_hash, model, prompt_version)
    conn.execute(
        """INSERT OR REPLACE INTO llm_cache (cache_key, query, context_hash, model, prompt_version, response_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
        (
            cache_key,
            query,
            context_hash,
            model,
            prompt_version,
            json.dumps(response, ensure_ascii=False),
        ),
    )
    conn.commit()
