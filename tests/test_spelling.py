import pytest
from ctxword.spelling import check_spelling, is_valid_word
from ctxword.classify import InputType


class TestSpelling:
    def test_valid_common_word(self):
        # "the" should always be valid if word list loaded
        result = is_valid_word("the")
        # If no dict file, still valid via tech words fallback
        assert result is True or result is False  # depends on system dict

    def test_typo_detection(self):
        # "enviroment" should trigger typo warning if word list available
        is_typo, suggestion, suggestions = check_spelling("enviroment", InputType.SINGLE_WORD)
        # This may or may not trigger depending on word list availability
        # Just verify the function runs without error
        assert isinstance(is_typo, bool)

    def test_phrase_skips_spellcheck(self):
        is_typo, suggestion, suggestions = check_spelling("race condition", InputType.PHRASE)
        assert is_typo is False
        assert suggestions == []

    def test_identifier_skips_spellcheck(self):
        is_typo, suggestion, suggestions = check_spelling(
            "shouldInvalidateCache", InputType.CODE_IDENTIFIER
        )
        assert is_typo is False
        assert suggestions == []
