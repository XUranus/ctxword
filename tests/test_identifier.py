import pytest
from ctxword.identifier import explain_identifier, _detect_identifier_style


class TestIdentifier:
    def test_explain_camel_case(self):
        result = explain_identifier("shouldInvalidateCache")
        assert result["identifier"] == "shouldInvalidateCache"
        assert result["words"] == ["should", "invalidate", "cache"]
        assert result["word_count"] == 3

    def test_explain_snake_case(self):
        result = explain_identifier("max_retry_count")
        assert result["identifier"] == "max_retry_count"
        assert result["words"] == ["max", "retry", "count"]

    def test_explain_single_word(self):
        result = explain_identifier("pending")
        assert result["words"] == ["pending"]
        assert result["word_count"] == 1


class TestIdentifierStyle:
    def test_camel_case(self):
        assert _detect_identifier_style("shouldInvalidateCache") == "camelCase"

    def test_pascal_case(self):
        assert _detect_identifier_style("HTTPResponse") == "PascalCase"

    def test_snake_case(self):
        assert _detect_identifier_style("max_retry_count") == "snake_case"

    def test_screaming_snake(self):
        assert _detect_identifier_style("MAX_RETRY") == "SCREAMING_SNAKE_CASE"

    def test_kebab_case(self):
        assert _detect_identifier_style("max-retry-count") == "kebab-case"
