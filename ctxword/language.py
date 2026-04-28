"""Language detection using simple heuristics."""

import re
from enum import StrEnum


class Language(StrEnum):
    ENGLISH = "en"
    CHINESE = "zh"
    MIXED = "mixed"
    UNKNOWN = "unknown"


CJK_RE = re.compile(r"[一-鿿㐀-䶿豈-﫿]")
LATIN_RE = re.compile(r"[a-zA-Z]{2,}")


def detect(text: str) -> Language:
    """Detect the primary language of the input text."""
    if not text:
        return Language.UNKNOWN

    has_cjk = bool(CJK_RE.search(text))
    has_latin = bool(LATIN_RE.search(text))

    if has_cjk and has_latin:
        return Language.MIXED
    if has_cjk:
        return Language.CHINESE
    if has_latin:
        return Language.ENGLISH

    return Language.UNKNOWN
