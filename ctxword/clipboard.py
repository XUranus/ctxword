"""Clipboard integration: reading system clipboard content."""

import subprocess
import shutil

from .config import ClipboardConfig
from .errors import ClipboardError


def _read_wayland() -> str:
    """Read clipboard using wl-paste (Wayland)."""
    try:
        result = subprocess.run(
            ["wl-paste", "--primary"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        result = subprocess.run(
            ["wl-paste"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    raise ClipboardError("Could not read clipboard via wl-paste")


def _read_x11() -> str:
    """Read clipboard using xclip or xsel (X11)."""
    for cmd in [["xclip", "-selection", "clipboard", "-o"],
                ["xclip", "-o"],
                ["xsel", "--clipboard", "--output"],
                ["xsel", "--output"]]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    raise ClipboardError("Could not read clipboard via xclip/xsel. Install xclip or xsel.")


def _read_pyperclip() -> str:
    """Read clipboard using pyperclip (cross-platform fallback)."""
    try:
        import pyperclip
        text = pyperclip.paste()
        if text and text.strip():
            return text.strip()
    except Exception as e:
        raise ClipboardError(f"Pyperclip failed: {e}")
    raise ClipboardError("Clipboard is empty or unreadable")


def read(config: ClipboardConfig | None = None) -> str:
    """Read text from the system clipboard.

    Tries multiple backends in order: wl-paste (Wayland), xclip/xsel (X11), pyperclip.
    """
    backend = config.backend if config else "auto"

    if backend == "wayland":
        return _read_wayland()
    elif backend == "x11":
        return _read_x11()
    elif backend == "pyperclip":
        return _read_pyperclip()

    # Auto-detect
    errors = []
    for method in [_read_wayland, _read_x11, _read_pyperclip]:
        try:
            return method()
        except ClipboardError as e:
            errors.append(str(e))

    raise ClipboardError(
        "Failed to read clipboard with any backend. "
        "Ensure wl-paste (Wayland), xclip/xsel (X11), or pyperclip is installed.\n"
        + "\n".join(errors)
    )
