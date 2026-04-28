import pytest
from ctxword.classify import classify, split_identifier, InputType


class TestClassify:
    def test_single_word(self):
        assert classify("pending") == InputType.SINGLE_WORD
        assert classify("hello") == InputType.SINGLE_WORD
        assert classify("race") == InputType.SINGLE_WORD

    def test_phrase(self):
        assert classify("race condition") == InputType.PHRASE
        assert classify("breaking change") == InputType.PHRASE
        assert classify("working tree") == InputType.PHRASE

    def test_sentence(self):
        assert classify("The promise is still pending.") == InputType.SENTENCE

    def test_camel_case(self):
        assert classify("shouldInvalidateCache") == InputType.CODE_IDENTIFIER
        assert classify("getUserProfile") == InputType.CODE_IDENTIFIER

    def test_pascal_case(self):
        assert classify("HTTPResponse") == InputType.CODE_IDENTIFIER

    def test_snake_case(self):
        assert classify("race_condition") == InputType.CODE_IDENTIFIER
        assert classify("max_retry_count") == InputType.CODE_IDENTIFIER

    def test_empty(self):
        assert classify("") == InputType.UNKNOWN
        assert classify("   ") == InputType.UNKNOWN

    def test_unknown(self):
        assert classify("123") == InputType.UNKNOWN


class TestSplitIdentifier:
    def test_camel_case(self):
        assert split_identifier("shouldInvalidateCache") == ["should", "invalidate", "cache"]

    def test_pascal_case(self):
        assert split_identifier("HTTPResponse") == ["h", "t", "t", "p", "response"]

    def test_snake_case(self):
        assert split_identifier("max_retry_count") == ["max", "retry", "count"]

    def test_screaming_snake(self):
        assert split_identifier("MAX_RETRY_COUNT") == ["max", "retry", "count"]

    def test_kebab_case(self):
        assert split_identifier("max-retry-count") == ["max", "retry", "count"]
