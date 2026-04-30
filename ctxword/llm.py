"""LLM client for OpenAI-compatible APIs."""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from .config import Config
from .errors import LLMError
from .paths import get_llm_dir
from .logging_config import get_logger

logger = get_logger("llm")

# Prompt versions for cache tracking
PROMPT_VERSION_EXPLAIN_WORD = "explain_word_v1"
PROMPT_VERSION_EXPLAIN_PHRASE = "explain_phrase_v1"
PROMPT_VERSION_EXPLAIN_IDENTIFIER = "explain_identifier_v1"

SYSTEM_PROMPT = """You are an English learning assistant for Chinese-speaking programmers.
Explain English words, phrases, and code identifiers in technical context.
Be concise and programmer-friendly. Keep all field values brief (1-3 sentences max).
Return ONLY valid JSON, no markdown, no code blocks. Ensure the JSON is complete."""


class LLMResponse(BaseModel):
    query: str = ""
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
        "Return a COMPLETE JSON object with these fields (keep values short):",
        "- normalized_query, lemma, part_of_speech (list)",
        "- meaning_zh, meaning_en (1 short sentence each)",
        "- context_explanation, technical_domain (list), technical_note",
        "- collocations (list of short phrases)",
        "- examples (list of {en, zh}, max 2)",
        "- common_mistakes (list, max 2)",
        "- cards (list of {type, front, back, tags}, max 3)",
        "",
        "IMPORTANT: Ensure your JSON response is complete and properly closed.",
    ])

    return "\n".join(parts)


def _get_prompt_version(input_type: str) -> str:
    if input_type == "code_identifier":
        return PROMPT_VERSION_EXPLAIN_IDENTIFIER
    if input_type == "phrase":
        return PROMPT_VERSION_EXPLAIN_PHRASE
    return PROMPT_VERSION_EXPLAIN_WORD


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "****" + key[-4:]


def _make_cache_key(query: str, context_hash: str | None, model: str, prompt_version: str) -> str:
    raw = f"{query}|{context_hash or ''}|{model}|{prompt_version}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _audit_save(filename: str, data: dict) -> None:
    """Save LLM request/response to audit directory."""
    try:
        dir_ = get_llm_dir()
        dir_.mkdir(parents=True, exist_ok=True)
        with open(dir_ / filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except Exception:
        pass  # audit save failure must not break the main flow


async def _call_api(
    url: str,
    api_key: str,
    payload: dict,
    config: Config,
) -> tuple[str, bool]:
    """Make a single API call. Returns (content, was_truncated)."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    model = payload.get("model", "unknown")
    logger.info("API call: model=%s url=%s max_tokens=%s",
                model, url, payload.get("max_tokens"))

    # Audit: save request (with key masked)
    audit_payload = {**payload, "_masked_key": _mask_key(api_key)}
    _audit_save(f"{ts}_request.json", audit_payload)

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
            detail = e.response.text[:500]
            logger.error("HTTP %s from %s: %s", e.response.status_code, url, detail)
            msg = (
                f"LLM API returned HTTP {e.response.status_code}\n"
                f"  URL: {url}\n"
                f"  Model: {config.llm.model}\n"
                f"  Response: {detail}"
            )
            if e.response.status_code == 404:
                msg += "\n  Hint: the API endpoint was not found. Check that base_url includes /v1 if required."
            elif e.response.status_code == 405:
                msg += "\n  Hint: this URL doesn't accept API requests — are you using the web UI address instead of the API endpoint?"
            elif e.response.status_code in (401, 403):
                msg += "\n  Hint: check that CTXWORD_OPENAI_KEY is set correctly."
            raise LLMError(msg)
        except httpx.ConnectError as e:
            logger.error("Connection refused: %s — %s", url, e)
            raise LLMError(
                f"Cannot connect to LLM API — connection refused or unreachable.\n"
                f"  URL: {url}\n"
                f"  Check that CTXWORD_OPENAI_BASE is correct.\n"
                f"  Detail: {e!r}"
            )
        except httpx.TimeoutException as e:
            logger.error("Request timed out: %s — %s", url, e)
            raise LLMError(
                f"LLM API request timed out after 30s.\n"
                f"  URL: {url}\n"
                f"  Model: {config.llm.model}\n"
                f"  Detail: {e!r}"
            )
        except httpx.RequestError as e:
            logger.error("Request failed: %s — %s (%s)", url, type(e).__name__, e)
            raise LLMError(
                f"LLM API request failed.\n"
                f"  URL: {url}\n"
                f"  Model: {config.llm.model}\n"
                f"  Error type: {type(e).__name__}\n"
                f"  Detail: {e!r}"
            )

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    finish_reason = data["choices"][0].get("finish_reason", "stop")

    # Audit: save response
    _audit_save(f"{ts}_response.json", data)

    return content, finish_reason == "length"


def _strip_markdown(content: str) -> str:
    """Strip markdown code block wrappers from LLM output."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def _recover_truncated_json(content: str) -> str | None:
    """Try to salvage truncated JSON by closing unclosed structures.

    Returns the repaired JSON string, or None if recovery is not possible.
    """
    # Scan to find unclosed structures
    stack: list[str] = []
    in_string = False
    escape_next = False

    for ch in content:
        if escape_next:
            escape_next = False
            continue
        if ch == "\\":
            escape_next = True
            continue
        if ch == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch in "{[":
            stack.append(ch)
        elif ch == "}":
            if stack and stack[-1] == "{":
                stack.pop()
        elif ch == "]":
            if stack and stack[-1] == "[":
                stack.pop()

    # Check if there's anything to recover
    if not in_string and not stack:
        return None  # content seems complete, nothing to repair

    # Build the repaired JSON
    repaired = content

    # Close any unclosed string
    if in_string:
        repaired += '"'

    # Close any unclosed brackets/braces in reverse order
    while stack:
        opener = stack.pop()
        repaired += "}" if opener == "{" else "]"

    # If we barely have anything useful, give up
    if len(repaired) < 10 or "{" not in repaired:
        return None

    return repaired


def _parse_json_content(content: str) -> dict:
    """Parse JSON from LLM content, with recovery for truncated responses.

    Returns parsed dict. Raises LLMError with details on failure.
    """
    content = _strip_markdown(content)

    parse_errors: list[str] = []

    # Attempt 1: direct parse (strict=False accepts control chars in strings)
    try:
        return json.loads(content, strict=False)
    except json.JSONDecodeError as e:
        parse_errors.append(f"direct parse: {e}")

    # Attempt 2: try recovery of truncated JSON
    recovered = _recover_truncated_json(content)
    if recovered:
        try:
            return json.loads(recovered, strict=False)
        except json.JSONDecodeError as e:
            parse_errors.append(f"recovery parse: {e}")

    raise LLMError(
        "Failed to parse LLM response as JSON.\n"
        f"  Errors: {'; '.join(parse_errors)}\n"
        f"  Raw (first 300 chars): {content[:300]}"
    )


def _has_backup(config: Config) -> bool:
    """Check if a backup model is configured."""
    return bool(
        config.llm.backup_api_key
        and config.llm.backup_base_url
        and config.llm.backup_model
    )


async def _try_explain_with_model(
    query: str,
    input_type: str,
    config: Config,
    user_prompt: str,
    api_key: str,
    model: str,
    base_url: str,
    label: str,
) -> dict[str, Any]:
    """Inner retry loop for a single model. label is "primary" or "backup"."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    max_tokens = config.llm.max_tokens

    last_content = ""
    for attempt in range(3):
        if attempt > 0:
            max_tokens = int(max_tokens * 1.5)
            logger.info("Retry attempt %d/3 for %s model (max_tokens=%d)",
                        attempt + 1, label, max_tokens)

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": config.llm.temperature,
            "max_tokens": max_tokens,
        }

        content, was_truncated = await _call_api(url, api_key, payload, config)
        last_content = content

        if was_truncated and attempt < 2:
            logger.warning("Response truncated (finish_reason=length), retrying (%s)",
                           label)
            continue

        try:
            parsed = _parse_json_content(content)
        except LLMError:
            if attempt < 2:
                logger.warning("JSON parse failed on attempt %d, retrying (%s)",
                               attempt + 1, label)
                continue
            raise

        try:
            validated = LLMResponse.model_validate(parsed)
        except ValidationError as e:
            if attempt < 2:
                logger.warning("Schema validation failed on attempt %d, retrying (%s): %s",
                               attempt + 1, label, e)
                continue
            raise LLMError(
                f"LLM response missing required fields after {attempt + 1} attempts "
                f"({label} model).\n"
                f"  Validation error: {e}\n"
                f"  Parsed: {json.dumps(parsed, ensure_ascii=False)[:300]}"
            )

        result = validated.model_dump()
        if not result.get("query"):
            result["query"] = query
        if not result.get("normalized_query"):
            result["normalized_query"] = query.lower()
        if not result.get("input_type") or result["input_type"] == "unknown":
            result["input_type"] = input_type
        logger.info("LLM response parsed successfully (%s model, attempt %d)",
                     label, attempt + 1)
        return result

    logger.error("%s model exhausted all retries", label)
    raise LLMError(
        f"Failed to get a valid LLM response from {label} model after 3 attempts.\n"
        f"  Last raw response (first 300 chars): {last_content[:300]}"
    )


async def explain(
    query: str,
    input_type: str,
    config: Config,
    context: str | None = None,
    context_hash: str | None = None,
    lemma: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Call the LLM to explain a word/phrase/identifier, with retry on truncation.

    Falls back to the backup model (if configured) when the primary fails.
    Returns a validated dict matching the LLMResponse schema.
    """
    if not config.llm.enabled:
        raise LLMError("LLM is disabled in config.")

    if api_key is None:
        raise LLMError(
            "API key not found. Set the CTXWORD_OPENAI_KEY environment variable."
        )

    prompt_version = _get_prompt_version(input_type)
    user_prompt = _build_user_prompt(query, input_type, context, lemma)

    # Try primary model
    primary_errors: list[str] = []
    try:
        return await _try_explain_with_model(
            query=query,
            input_type=input_type,
            config=config,
            user_prompt=user_prompt,
            api_key=api_key,
            model=config.llm.model,
            base_url=config.llm.base_url,
            label="primary",
        )
    except LLMError as e:
        logger.warning("Primary model failed: %s", e)
        primary_errors.append(str(e))

    # Try backup model if primary failed
    if _has_backup(config):
        logger.info("Falling back to backup model: %s", config.llm.backup_model)
        try:
            return await _try_explain_with_model(
                query=query,
                input_type=input_type,
                config=config,
                user_prompt=user_prompt,
                api_key=config.llm.backup_api_key,
                model=config.llm.backup_model,
                base_url=config.llm.backup_base_url,
                label="backup",
            )
        except LLMError as e:
            raise LLMError(
                "All LLM models failed.\n"
                f"  Primary error: {primary_errors[0] if primary_errors else 'unknown'}\n"
                f"  Backup error: {e}"
            )

    # No backup configured — re-raise the primary error
    raise LLMError(primary_errors[0] if primary_errors else "Unknown LLM error")


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
            logger.info("Cache hit for %r", query)
            return json.loads(row["response_json"])
        except json.JSONDecodeError:
            logger.warning("Cache entry corrupt for %r", query)
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
