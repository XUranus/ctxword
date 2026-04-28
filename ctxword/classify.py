"""Input classification: determines whether input is a word, phrase, identifier, etc."""

import re
from enum import StrEnum


class InputType(StrEnum):
    SINGLE_WORD = "single_word"
    PHRASE = "phrase"
    SENTENCE = "sentence"
    CODE_IDENTIFIER = "code_identifier"
    MIXED_TEXT = "mixed_text"
    UNKNOWN = "unknown"


CAMEL_CASE_RE = re.compile(r"^[a-z]+(?:[A-Z][a-z]*)+$")
PASCAL_CASE_RE = re.compile(r"^[A-Z][a-z]*(?:[A-Z][a-z]*)+$")
SNAKE_CASE_RE = re.compile(r"^[a-z]+(?:_[a-z]+)+$")
KEBAB_CASE_RE = re.compile(r"^[a-z]+(?:-[a-z]+)+$")
SCREAMING_SNAKE_RE = re.compile(r"^[A-Z]+(?:_[A-Z]+)+$")
IDENTIFIER_MIXED_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def classify(query: str) -> InputType:
    """Classify the input query into one of the input types."""
    query = query.strip()

    if not query:
        return InputType.UNKNOWN

    # Multi-word: check spaces
    word_count = len(query.split())
    if word_count > 1:
        # Contains sentence-ending punctuation -> sentence
        if any(c in query for c in ".!?;:"):
            return InputType.SENTENCE
        # Short multi-word without punctuation -> phrase
        if word_count <= 5:
            return InputType.PHRASE
        # Longer multi-word without punctuation -> sentence
        if word_count > 10:
            return InputType.SENTENCE
        return InputType.PHRASE

    # Single token analysis
    token = query

    # Check for code identifiers
    if CAMEL_CASE_RE.match(token):
        return InputType.CODE_IDENTIFIER
    if PASCAL_CASE_RE.match(token):
        return InputType.CODE_IDENTIFIER
    if SNAKE_CASE_RE.match(token):
        return InputType.CODE_IDENTIFIER
    if SCREAMING_SNAKE_RE.match(token):
        return InputType.CODE_IDENTIFIER
    if KEBAB_CASE_RE.match(token):
        return InputType.CODE_IDENTIFIER

    # Plain single word (alphabetic only)
    if token.isalpha():
        return InputType.SINGLE_WORD

    # Mixed alphanumeric identifier-like
    if IDENTIFIER_MIXED_RE.match(token):
        return InputType.CODE_IDENTIFIER

    return InputType.UNKNOWN


def split_identifier(identifier: str) -> list[str]:
    """Split a code identifier into component words."""
    # Handle snake_case and screaming snake case
    if "_" in identifier:
        return [w.lower() for w in identifier.split("_") if w]

    # Handle kebab-case
    if "-" in identifier:
        return [w.lower() for w in identifier.split("-") if w]

    # Handle camelCase and PascalCase
    words: list[str] = []
    current: list[str] = []
    for ch in identifier:
        if ch.isupper() and current:
            words.append("".join(current).lower())
            current = [ch]
        else:
            current.append(ch)
    if current:
        words.append("".join(current).lower())

    return [w for w in words if w]
