"""Schema-aware IO helpers for Anyon Condense payloads."""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict

from .exceptions import DataIOError, SchemaError, ValidationError
from .schema import validate

JsonDict = Dict[str, Any]


def _to_path(path_like: str | pathlib.Path) -> pathlib.Path:
    """Normalize *path_like* to an absolute :class:`pathlib.Path`."""

    return pathlib.Path(path_like).expanduser().resolve()


def _read_json(path: pathlib.Path) -> JsonDict:
    """Read UTF-8 JSON file into a dict, raising :class:`DataIOError` on failure."""

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        raise DataIOError(
            f"Failed to read file: {path} ({exc.__class__.__name__})"
        ) from exc

    try:
        payload = json.loads(text)
    except Exception as exc:  # pragma: no cover - defensive
        raise DataIOError(
            f"Invalid JSON in file: {path} ({exc.__class__.__name__})"
        ) from exc

    if not isinstance(payload, dict):
        raise DataIOError(f"Top-level JSON must be an object: {path}")

    return payload


def _write_json(path: pathlib.Path, payload: JsonDict) -> None:
    """Serialise *payload* to JSON, raising :class:`DataIOError` on failure."""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except Exception as exc:  # pragma: no cover - defensive
        raise DataIOError(
            f"Failed to write JSON to: {path} ({exc.__class__.__name__})"
        ) from exc


def _validate_or_raise(payload: JsonDict, schema_name: str) -> None:
    """Run ``validate`` and normalise :class:`SchemaError` into ``ValidationError``."""

    try:
        validate(payload, schema_name)
    except SchemaError as exc:
        raise ValidationError(str(exc)) from exc


def load_mfusion_input(path: str | pathlib.Path) -> JsonDict:
    """Load and validate an ``ac-mfusion`` input document."""

    resolved = _to_path(path)
    payload = _read_json(resolved)
    _validate_or_raise(payload, "mfusion_input.schema.json")
    return payload


def load_umtc_input(path: str | pathlib.Path) -> JsonDict:
    """Load and validate an ``ac-umtc`` input document."""

    resolved = _to_path(path)
    payload = _read_json(resolved)
    _validate_or_raise(payload, "umtc_input.schema.json")
    return payload


def write_umtc_output(path: str | pathlib.Path, payload: JsonDict) -> None:
    """Validate and write an ``ac-umtc`` output document."""

    _validate_or_raise(payload, "umtc_output.schema.json")
    resolved = _to_path(path)
    _write_json(resolved, payload)


__all__ = [
    "load_mfusion_input",
    "load_umtc_input",
    "write_umtc_output",
]
