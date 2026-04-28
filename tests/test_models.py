import json
import pytest
from ctxword.models import Lookup, Entry, ReviewCard, ReviewLog, LLMCache, now_iso


class TestLookup:
    def test_create(self):
        l = Lookup(query="pending", input_type="single_word", language="en")
        assert l.query == "pending"
        assert l.input_type == "single_word"
        assert l.status == "saved"
        assert l.created_at is not None

    def test_defaults(self):
        l = Lookup(query="test")
        assert l.id is None
        assert l.normalized_query is None
        assert l.input_type == "unknown"


class TestEntry:
    def test_from_llm_response(self):
        response = {
            "query": "pending",
            "lemma": "pending",
            "part_of_speech": ["adjective"],
            "meaning_zh": "尚未完成",
            "meaning_en": "not yet completed",
            "context_explanation": "In async programming...",
            "technical_domain": ["programming", "async"],
            "technical_note": "A Promise can be pending...",
            "collocations": ["pending request", "pending promise"],
            "examples": [{"en": "The request is pending.", "zh": "请求待处理。"}],
            "common_mistakes": ["Don't translate literally."],
            "cards": [{"type": "context", "front": "...", "back": "...", "tags": ["async"]}],
        }

        entry = Entry.from_llm_response(1, response)
        assert entry.lookup_id == 1
        assert entry.lemma == "pending"
        assert isinstance(entry.part_of_speech, str)
        assert json.loads(entry.part_of_speech) == ["adjective"]
        assert json.loads(entry.technical_domain) == ["programming", "async"]

    def test_from_llm_response_none_fields(self):
        response = {
            "query": "test",
            "lemma": "test",
            "part_of_speech": None,
            "meaning_zh": "",
            "meaning_en": "",
        }
        entry = Entry.from_llm_response(1, response)
        assert entry.part_of_speech is None
        assert entry.meaning_zh == ""


class TestReviewCard:
    def test_create(self):
        card = ReviewCard(
            entry_id=1,
            card_type="meaning",
            front="What does pending mean?",
            back="尚未完成",
        )
        assert card.entry_id == 1
        assert card.state == "new"
        assert card.ease == 2.5
        assert card.reps == 0


class TestReviewLog:
    def test_create(self):
        log = ReviewLog(card_id=1, rating="good")
        assert log.card_id == 1
        assert log.rating == "good"
        assert log.reviewed_at is not None


class TestLLMCache:
    def test_create(self):
        cache = LLMCache(
            cache_key="abc123",
            query="pending",
            response_json='{"result": "ok"}',
        )
        assert cache.cache_key == "abc123"
        assert cache.query == "pending"
