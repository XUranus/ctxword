"""Configuration from environment variables. No config file needed."""

import os
from dataclasses import dataclass, field


@dataclass
class GeneralConfig:
    language: str = "zh-CN"
    auto_save: bool = True
    max_cards_per_lookup: int = 3


@dataclass
class StorageConfig:
    database_path: str = ""


@dataclass
class LLMConfig:
    enabled: bool = True
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.2
    max_tokens: int = 2048
    cache: bool = True


@dataclass
class ReviewConfig:
    enabled: bool = True
    scheduler: str = "simple"
    new_cards_per_day: int = 20
    review_cards_per_day: int = 100


@dataclass
class ClipboardConfig:
    backend: str = "auto"


@dataclass
class AnkiConfig:
    enabled: bool = False
    default_deck: str = "ctxword"
    export_format: str = "tsv"


@dataclass
class Config:
    general: GeneralConfig = field(default_factory=GeneralConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    review: ReviewConfig = field(default_factory=ReviewConfig)
    clipboard: ClipboardConfig = field(default_factory=ClipboardConfig)
    anki: AnkiConfig = field(default_factory=AnkiConfig)


def load_config() -> Config:
    return Config(
        general=GeneralConfig(
            language=os.environ.get("CTXWORD_LANG", "zh-CN"),
        ),
        llm=LLMConfig(
            enabled=os.environ.get("CTXWORD_LLM_ENABLED", "1") not in ("0", "false", "no"),
            base_url=os.environ.get("CTXWORD_OPENAI_BASE", "https://api.openai.com/v1"),
            api_key=os.environ.get("CTXWORD_OPENAI_KEY", ""),
            model=os.environ.get("CTXWORD_MODEL", "gpt-3.5-turbo"),
            temperature=float(os.environ.get("CTXWORD_TEMPERATURE", "0.2")),
            max_tokens=int(os.environ.get("CTXWORD_MAX_TOKENS", "2048")),
            cache=os.environ.get("CTXWORD_CACHE", "1") not in ("0", "false", "no"),
        ),
        review=ReviewConfig(
            enabled=os.environ.get("CTXWORD_REVIEW_ENABLED", "1") not in ("0", "false", "no"),
        ),
    )
