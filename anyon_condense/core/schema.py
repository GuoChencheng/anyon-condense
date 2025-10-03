"""Schema loading and validation helpers."""

from __future__ import annotations

import json
import pathlib
from functools import lru_cache
from typing import Any

from jsonschema import Draft202012Validator

# Repository root: .../anyon-condense/
_ROOT = pathlib.Path(__file__).resolve().parents[2]
_SCHEMAS_DIR = _ROOT / "schemas"


@lru_cache(maxsize=64)
def _load_schema_text(schema_name: str) -> str:
    path = _SCHEMAS_DIR / schema_name
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    return path.read_text(encoding="utf-8")


@lru_cache(maxsize=64)
def _get_validator(schema_name: str) -> Draft202012Validator:
    schema = json.loads(_load_schema_text(schema_name))
    return Draft202012Validator(schema)


def validate(payload: dict[str, Any], schema_name: str) -> None:
    """Validate a payload against one of the bundled JSON schemas."""

    _get_validator(schema_name).validate(payload)
