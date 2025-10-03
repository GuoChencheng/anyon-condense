"""Project-wide logging helpers."""

from __future__ import annotations

import logging
import os
from typing import Optional

_INITIALIZED = False


def _resolve_level(level: Optional[str]) -> int:
    if level is not None:
        return getattr(logging, level.upper(), logging.INFO)
    level_name = os.environ.get("AC_LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


def init_logging(level: Optional[str] = None) -> None:
    """Initialise root logger once with consistent formatting."""

    global _INITIALIZED
    if _INITIALIZED:
        return

    resolved_level = _resolve_level(level)
    root_logger = logging.getLogger()
    root_logger.setLevel(resolved_level)

    handler = logging.StreamHandler()
    handler.setLevel(resolved_level)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    _INITIALIZED = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured with project defaults."""

    init_logging()
    return logging.getLogger(name)


__all__ = ["get_logger", "init_logging"]
