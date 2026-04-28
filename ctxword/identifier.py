"""Code identifier analysis: splitting and explaining identifiers."""

from .classify import split_identifier, InputType


def explain_identifier(identifier: str) -> dict:
    """Analyze a code identifier and return structured info.

    Returns a dict with:
    - identifier: original identifier
    - words: split component words
    - suggested_explanation: a suggested explanation of what this identifier means
    """
    words = split_identifier(identifier)

    # Build a suggested explanation from the split words
    # This is heuristic; LLM would provide better results
    return {
        "identifier": identifier,
        "type": _detect_identifier_style(identifier),
        "words": words,
        "word_count": len(words),
    }


def _detect_identifier_style(identifier: str) -> str:
    if "_" in identifier:
        if identifier.isupper():
            return "SCREAMING_SNAKE_CASE"
        return "snake_case"
    if "-" in identifier:
        return "kebab-case"
    if identifier[0].isupper():
        return "PascalCase"
    return "camelCase"
