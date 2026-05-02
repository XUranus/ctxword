"""Autocomplete: fast prefix-based word completion for shell tab completion.

The shell completion scripts use grep on a cached word list file, so Tab
completion is instant. This module builds that cache and provides a Python
path for the hidden `_complete` CLI command.
"""

import bisect

from .paths import get_data_dir


def _load_words() -> list[str]:
    """Load and return a sorted list of all known words.

    Sources: system word list, built-in common words, and tech terms.
    """
    from .wordlist_data import BUILTIN_WORDS

    words: set[str] = set(BUILTIN_WORDS)

    wordlist_paths = [
        "/usr/share/dict/words",
        "/usr/dict/words",
        "/usr/share/dict/american-english",
        "/usr/share/dict/british-english",
    ]
    for path in wordlist_paths:
        try:
            with open(path) as f:
                for line in f:
                    w = line.strip().lower()
                    if w and w.isalpha() and len(w) >= 2:
                        words.add(w)
            break
        except FileNotFoundError:
            continue

    return sorted(words)


def _cache_path() -> str:
    return str(get_data_dir() / "completions.txt")


def build_cache() -> int:
    """Build the completion word list cache file. Returns word count."""
    words = _load_words()
    path = _cache_path()
    with open(path, "w") as f:
        for w in words:
            f.write(w + "\n")
    return len(words)


def complete(prefix: str, limit: int = 50) -> list[str]:
    """Return words starting with prefix (case-insensitive). Uses cache if available."""
    prefix = prefix.lower().strip()
    if not prefix:
        return []

    # Try cache first (fastest)
    cache = _cache_path()
    try:
        import os
        if os.path.getsize(cache) > 0:
            return _complete_from_cache(prefix, limit)
    except (FileNotFoundError, OSError):
        pass

    # Fall back to in-memory search
    words = _load_words()
    i = bisect.bisect_left(words, prefix)
    results = []
    for word in words[i:]:
        if not word.startswith(prefix):
            break
        results.append(word)
        if len(results) >= limit:
            break
    return results


def _complete_from_cache(prefix: str, limit: int) -> list[str]:
    """Grep the cache file for prefix matches (fast, used by shell scripts too)."""
    results: list[str] = []
    with open(_cache_path()) as f:
        for line in f:
            word = line.rstrip("\n")
            if word.startswith(prefix):
                results.append(word)
                if len(results) >= limit:
                    break
            elif word > prefix:
                # File is sorted, we can stop early
                break
    return results
