"""Morphology analysis: lemmatization and part-of-speech detection.

Uses simple rule-based approaches for MVP. Can be extended with NLTK/spaCy later.
"""

import re

# Irregular forms mapping
_IRREGULAR_LEMMAS: dict[str, str] = {
    # Verbs
    "ran": "run",
    "running": "run",
    "ran": "run",
    "went": "go",
    "gone": "go",
    "going": "go",
    "been": "be",
    "was": "be",
    "were": "be",
    "being": "be",
    "had": "have",
    "has": "have",
    "having": "have",
    "did": "do",
    "done": "do",
    "doing": "do",
    "made": "make",
    "making": "make",
    "taken": "take",
    "took": "take",
    "taking": "take",
    "written": "write",
    "wrote": "write",
    "writing": "write",
    "given": "give",
    "gave": "give",
    "giving": "give",
    "seen": "see",
    "saw": "see",
    "known": "know",
    "knew": "know",
    "thought": "think",
    "thinking": "think",
    "meant": "mean",
    "meaning": "mean",
    "read": "read",
    "reading": "read",
    "set": "set",
    "setting": "set",
    "put": "put",
    "putting": "put",
    "built": "build",
    "building": "build",
    "found": "find",
    "finding": "find",
    "left": "leave",
    "leaving": "leave",
    "brought": "bring",
    "bringing": "bring",
    "bought": "buy",
    "buying": "buy",
    "caught": "catch",
    "catching": "catch",
    "chosen": "choose",
    "chose": "choose",
    "choosing": "choose",
    "broken": "break",
    "broke": "break",
    "breaking": "break",
    "spoken": "speak",
    "spoke": "speak",
    "speaking": "speak",
    "eaten": "eat",
    "ate": "eat",
    "eating": "eat",
    "driven": "drive",
    "drove": "drive",
    "driving": "drive",
    "drawn": "draw",
    "drew": "draw",
    "drawing": "draw",
    "flown": "fly",
    "flew": "fly",
    "flying": "fly",
    "grown": "grow",
    "grew": "grow",
    "growing": "grow",
    "hidden": "hide",
    "hid": "hide",
    "hiding": "hide",
    "held": "hold",
    "holding": "hold",
    "kept": "keep",
    "keeping": "keep",
    "led": "lead",
    "leading": "lead",
    "lost": "lose",
    "losing": "lose",
    "paid": "pay",
    "paying": "pay",
    "said": "say",
    "saying": "say",
    "sent": "send",
    "sending": "send",
    "shown": "show",
    "showed": "show",
    "showing": "show",
    "slept": "sleep",
    "sleeping": "sleep",
    "stood": "stand",
    "standing": "stand",
    "stuck": "stick",
    "sticking": "stick",
    "taught": "teach",
    "teaching": "teach",
    "told": "tell",
    "telling": "tell",
    "thrown": "throw",
    "threw": "throw",
    "throwing": "throw",
    "understood": "understand",
    "understanding": "understand",
    "worn": "wear",
    "wore": "wear",
    "wearing": "wear",
    "won": "win",
    "winning": "win",

    # Nouns
    "children": "child",
    "mice": "mouse",
    "geese": "goose",
    "teeth": "tooth",
    "feet": "foot",
    "men": "man",
    "women": "woman",
    "people": "person",
    "indices": "index",
    "indexes": "index",
    "matrices": "matrix",
    "vertices": "vertex",
    "appendices": "appendix",
    "criteria": "criterion",
    "phenomena": "phenomenon",
    "data": "datum",
    "axes": "axis",
    "analyses": "analysis",
    "theses": "thesis",
    "hypotheses": "hypothesis",
    "diagnoses": "diagnosis",
    "crises": "crisis",
    "bases": "basis",

    # Adjectives
    "better": "good",
    "best": "good",
    "worse": "bad",
    "worst": "bad",
    "more": "much",
    "most": "much",
    "less": "little",
    "least": "little",
}


# Common inflection suffix rules: (pattern, replacement, expected POS)
_SUFFIX_RULES: list[tuple[str, str, str]] = [
    # Verb inflections
    (r"ies$", "y", "verb"),          # carries -> carry
    (r"ies$", "ie", "verb"),         # dies -> die
    (r"es$", "", "verb"),            # watches -> watch
    (r"sses$", "ss", "verb"),        # crosses -> cross
    (r"ing$", "", "verb"),           # running -> run
    (r"ing$", "e", "verb"),          # making -> make
    (r"ed$", "", "verb"),            # walked -> walk
    (r"ed$", "e", "verb"),           # liked -> like
    (r"ied$", "y", "verb"),          # carried -> carry
    (r"ed$", "", "adjective"),       # interested -> interest (past participle as adj)

    # Noun plurals
    (r"sses$", "ss", "noun"),        # classes -> class
    (r"xes$", "x", "noun"),          # boxes -> box
    (r"ches$", "ch", "noun"),        # matches -> match
    (r"shes$", "sh", "noun"),        # dishes -> dish
    (r"s$", "", "noun"),             # cats -> cat
    (r"ies$", "y", "noun"),          # cities -> city
    (r"ves$", "f", "noun"),          # wolves -> wolf
    (r"ves$", "fe", "noun"),         # lives -> life

    # Adjective forms
    (r"est$", "", "adjective"),      # biggest -> big
    (r"est$", "e", "adjective"),     # largest -> large
    (r"er$", "", "adjective"),       # bigger -> big
    (r"er$", "e", "adjective"),      # larger -> large
    (r"iest$", "y", "adjective"),    # happiest -> happy
    (r"ier$", "y", "adjective"),     # happier -> happy

    # Adverb forms
    (r"ly$", "", "adverb"),          # quickly -> quick
    (r"ily$", "y", "adverb"),        # happily -> happy
]


def _apply_suffix_rules(word: str) -> list[tuple[str, str]]:
    """Apply suffix removal rules and return possible (lemma, pos) pairs."""
    results: list[tuple[str, str]] = []
    word_lower = word.lower()

    for pattern, replacement, pos in _SUFFIX_RULES:
        m = re.search(pattern, word_lower)
        if m:
            lemma = re.sub(pattern, replacement, word_lower)
            if len(lemma) >= 2:  # Don't reduce to single letter
                results.append((lemma, pos))

    return results


def get_lemma(word: str) -> str | None:
    """Get the base form (lemma) of a word.

    Returns None if no lemma could be determined, or the word itself if it appears to be a base form.
    """
    word_lower = word.lower()

    # Check irregular forms first
    if word_lower in _IRREGULAR_LEMMAS:
        return _IRREGULAR_LEMMAS[word_lower]

    # If the word is short (<= 4 chars), it's likely already a base form
    if len(word_lower) <= 4:
        return word_lower

    # Apply suffix rules
    candidates = _apply_suffix_rules(word)
    if candidates:
        # Return the first candidate's lemma
        return candidates[0][0]

    return word_lower


def get_pos(word: str) -> list[str]:
    """Guess possible parts of speech for a word."""
    word_lower = word.lower()

    # Check irregular forms to determine POS
    # This is a heuristic - in practice, POS is highly context-dependent

    results: list[str] = []

    # Suffix-based POS detection
    if word_lower.endswith("ing"):
        results.append("verb")
        results.append("noun")  # gerund
    elif word_lower.endswith("ed"):
        results.append("verb")
        results.append("adjective")
    elif word_lower.endswith("ly"):
        results.append("adverb")
    elif word_lower.endswith("tion") or word_lower.endswith("sion"):
        results.append("noun")
    elif word_lower.endswith("ness"):
        results.append("noun")
    elif word_lower.endswith("ment"):
        results.append("noun")
    elif word_lower.endswith("able") or word_lower.endswith("ible"):
        results.append("adjective")
    elif word_lower.endswith("ful"):
        results.append("adjective")
    elif word_lower.endswith("ous"):
        results.append("adjective")
    elif word_lower.endswith("ize") or word_lower.endswith("ise"):
        results.append("verb")
    elif word_lower.endswith("ify"):
        results.append("verb")

    # Check suffix rule results
    suffix_results = _apply_suffix_rules(word)
    for _, pos in suffix_results:
        if pos not in results:
            results.append(pos)

    return results if results else ["unknown"]


def analyze(word: str) -> dict:
    """Perform full morphological analysis of a word.

    Returns a dict with lemma, pos, and related forms.
    """
    lemma = get_lemma(word)
    pos = get_pos(word)

    return {
        "word": word,
        "lemma": lemma,
        "pos": pos,
        "is_base_form": word.lower() == lemma if lemma else None,
    }
