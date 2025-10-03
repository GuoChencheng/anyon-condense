"""Project-wide logging helpers with unified formatting."""

from __future__ import annotations

import logging
from typing import Optional

_INITIALIZED = False
_FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def _resolve_level(level: Optional[str]) -> int:
    if isinstance(level, str):
        name = level.upper()
        return getattr(logging, name, logging.INFO)
    return logging.INFO


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a logger configured with the project's default handler/format."""

    global _INITIALIZED

    root = logging.getLogger()
    if not _INITIALIZED:
        desired_level = _resolve_level(level)

        handler = next(
            (h for h in root.handlers if getattr(h, "_ac_default", False)),
            None,
        )
        if handler is None:
            handler = logging.StreamHandler()
            handler._ac_default = True  # type: ignore[attr-defined]
            root.addHandler(handler)

        handler.setLevel(desired_level)
        handler.setFormatter(logging.Formatter(_FMT))
        root.setLevel(desired_level)

        _INITIALIZED = True

    return logging.getLogger(name)


__all__ = ["get_logger"]
