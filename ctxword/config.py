import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from . import paths
from .errors import ConfigError


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
    provider: str = "openai_compatible"
    base_url: str = "https://api.openai.com/v1"
    api_key_env: str = "CTXWORD_API_KEY"
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


DEFAULT_CONFIG = Config()


def _parse_general(data: dict) -> GeneralConfig:
    return GeneralConfig(
        language=data.get("language", "zh-CN"),
        auto_save=data.get("auto_save", True),
        max_cards_per_lookup=data.get("max_cards_per_lookup", 3),
    )


def _parse_storage(data: dict) -> StorageConfig:
    return StorageConfig(
        database_path=data.get("database_path", ""),
    )


def _parse_llm(data: dict) -> LLMConfig:
    return LLMConfig(
        enabled=data.get("enabled", True),
        provider=data.get("provider", "openai_compatible"),
        base_url=data.get("base_url", "https://api.openai.com/v1"),
        api_key_env=data.get("api_key_env", "CTXWORD_API_KEY"),
        model=data.get("model", "gpt-3.5-turbo"),
        temperature=data.get("temperature", 0.2),
        max_tokens=data.get("max_tokens", 1200),
        cache=data.get("cache", True),
    )


def _parse_review(data: dict) -> ReviewConfig:
    return ReviewConfig(
        enabled=data.get("enabled", True),
        scheduler=data.get("scheduler", "simple"),
        new_cards_per_day=data.get("new_cards_per_day", 20),
        review_cards_per_day=data.get("review_cards_per_day", 100),
    )


def _parse_clipboard(data: dict) -> ClipboardConfig:
    return ClipboardConfig(
        backend=data.get("backend", "auto"),
    )


def _parse_anki(data: dict) -> AnkiConfig:
    return AnkiConfig(
        enabled=data.get("enabled", False),
        default_deck=data.get("default_deck", "ctxword"),
        export_format=data.get("export_format", "tsv"),
    )


def load_config(config_path: Path | None = None) -> Config:
    if config_path is None:
        config_path = paths.get_config_path()

    if not config_path.exists():
        return DEFAULT_CONFIG

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        raise ConfigError(f"Failed to parse config file: {e}")

    return Config(
        general=_parse_general(data.get("general", {})),
        storage=_parse_storage(data.get("storage", {})),
        llm=_parse_llm(data.get("llm", {})),
        review=_parse_review(data.get("review", {})),
        clipboard=_parse_clipboard(data.get("clipboard", {})),
        anki=_parse_anki(data.get("anki", {})),
    )


def get_api_key(config: Config) -> str | None:
    return os.environ.get(config.llm.api_key_env)
