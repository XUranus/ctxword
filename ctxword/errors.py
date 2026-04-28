class CtxwordError(Exception):
    """Base exception for ctxword."""
    pass


class ConfigError(CtxwordError):
    """Configuration-related errors."""
    pass


class DatabaseError(CtxwordError):
    """Database-related errors."""
    pass


class LookupError(CtxwordError):
    """Lookup-related errors."""
    pass


class LLMError(CtxwordError):
    """LLM API related errors."""
    pass


class SpellCheckError(CtxwordError):
    """Spell check related errors."""
    pass


class ClipboardError(CtxwordError):
    """Clipboard access errors."""
    pass


class ExportError(CtxwordError):
    """Export related errors."""
    pass
