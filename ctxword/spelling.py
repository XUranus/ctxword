"""Spelling check and typo detection using rapidfuzz and a basic word list."""

from rapidfuzz import process, fuzz

from .classify import InputType

# Common English words - a minimal set for MVP. In production, load from a word list file.
_COMMON_WORDS: set[str] = set()

# Common programming/technical words that may not be in standard dictionaries
_TECH_WORDS: set[str] = {
    "async", "await", "promise", "callback", "middleware", "endpoint",
    "namespace", "runtime", "serializer", "deserialize", "memoize",
    "invalidate", "refactor", "destructure", "polyfill", "shim",
    "throttle", "debounce", "idempotent", "orthogonal", "canonical",
    "immutable", "mutable", "transpile", "minify", "uglify",
    "repo", "init", "config", "enum", "param", "args", "kwargs",
    "iterable", "awaitable", "thenable", "subclass", "superclass",
    "lifecycle", "directive", "decorator", "singleton", "factory",
    "observer", "mutex", "semaphore", "deadlock", "livelock",
    "backprop", "overfit", "underfit", "tokenize", "normalize",
    "pending", "mounted", "resolved", "rejected", "fulfilled",
    "panic", "kernel", "driver", "daemon", "socket", "buffer",
    "cache", "flush", "purge", "evict", "prefetch", "lookaside",
    "commit", "checkout", "rebase", "stash", "bisect", "cherry-pick",
    "race", "condition", "deadlock", "starvation", "contention",
}


def _ensure_word_list() -> set[str]:
    """Load or build the word list. Returns the combined word set."""
    if _COMMON_WORDS:
        return _COMMON_WORDS

    # Try to load from common Unix word list locations
    wordlist_paths = [
        "/usr/share/dict/words",
        "/usr/dict/words",
        "/usr/share/dict/american-english",
        "/usr/share/dict/british-english",
    ]

    for path in wordlist_paths:
        try:
            with open(path) as f:
                words = {line.strip().lower() for line in f if line.strip()}
                _COMMON_WORDS.update(words)
            break
        except FileNotFoundError:
            continue

    # Always include tech words
    _COMMON_WORDS.update(_TECH_WORDS)
    return _COMMON_WORDS


def is_valid_word(word: str) -> bool:
    """Check if a word appears in the known word list."""
    words = _ensure_word_list()
    return word.lower() in words


def suggest(word: str, limit: int = 3) -> list[tuple[str, float]]:
    """Suggest corrections for a potentially misspelled word.

    Returns a list of (word, score) tuples sorted by similarity.
    """
    words = _ensure_word_list()
    if not words:
        return []

    candidates = list(words)
    results = process.extract(
        word.lower(), candidates, scorer=fuzz.ratio, limit=limit
    )
    return [(match, score) for match, score, _ in results]


def check_spelling(query: str, input_type: InputType) -> tuple[bool, str | None, list[tuple[str, float]]]:
    """Check spelling of a query.

    Returns (is_typo, suggested_word, list_of_suggestions).
    - is_typo: True if the word is likely misspelled
    - suggested_word: The best suggestion (None if no suggestions)
    - list_of_suggestions: All suggestions with scores
    """
    # Only check single words
    if input_type != InputType.SINGLE_WORD:
        return False, None, []

    # Skip if the word is valid
    if is_valid_word(query):
        return False, None, []

    # Word not found - get suggestions
    suggestions = suggest(query, limit=3)

    if not suggestions:
        return False, None, []

    best_match, best_score = suggestions[0]

    # Only flag as typo if we have a close match
    if best_score >= 80:
        return True, best_match, suggestions

    return False, None, []
