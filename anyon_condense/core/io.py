"""Schema-aware IO helpers for Anyon Condense payloads."""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict

from .exceptions import DataIOError, SchemaError, ValidationError
from .logging import get_logger
from .schema import validate

JsonDict = Dict[str, Any]

logger = get_logger(__name__)


def _to_path(path_like: str | pathlib.Path) -> pathlib.Path:
    """Normalize *path_like* to an absolute :class:`pathlib.Path`."""

    return pathlib.Path(path_like).expanduser().resolve()


def _read_json(path: pathlib.Path) -> JsonDict:
    """Read UTF-8 JSON file into a dict, raising :class:`DataIOError` on failure."""

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("[ACIO01] read_error path=%s exc=%s", path, exc.__class__.__name__)
        raise DataIOError(
            f"[ACIO01] read_error path={path} exc={exc.__class__.__name__}"
        ) from exc

    try:
        payload = json.loads(text)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(
            "[ACIO02] json_decode_error path=%s exc=%s", path, exc.__class__.__name__
        )
        raise DataIOError(
            f"[ACIO02] json_decode_error path={path} exc={exc.__class__.__name__}"
        ) from exc

    if not isinstance(payload, dict):
        logger.error("[ACIO03] not_object_error path=%s", path)
        raise DataIOError(f"[ACIO03] not_object_error path={path}")

    return payload


def _write_json(path: pathlib.Path, payload: JsonDict) -> None:
    """Serialise *payload* to JSON, raising :class:`DataIOError` on failure."""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(
            "[ACIO04] write_error path=%s exc=%s", path, exc.__class__.__name__
        )
        raise DataIOError(
            f"[ACIO04] write_error path={path} exc={exc.__class__.__name__}"
        ) from exc


def _validate_or_raise(payload: JsonDict, schema_name: str) -> None:
    """Run ``validate`` and normalise :class:`SchemaError` into ``ValidationError``."""

    try:
        validate(payload, schema_name)
    except SchemaError as exc:
        logger.error(
            "[ACVAL01] schema_validation_error schema=%s msg=%s", schema_name, exc
        )
        raise ValidationError(f"[ACVAL01] {exc}") from exc


def load_mfusion_input(path: str | pathlib.Path) -> JsonDict:
    """Load and validate an ``ac-mfusion`` input document."""

    resolved = _to_path(path)
    logger.debug("load_mfusion_input path=%s", resolved)
    payload = _read_json(resolved)
    _validate_or_raise(payload, "mfusion_input.schema.json")
    logger.debug("load_mfusion_input.ok path=%s", resolved)
    return payload


def load_umtc_input(path: str | pathlib.Path) -> JsonDict:
    """Load and validate an ``ac-umtc`` input document."""

    resolved = _to_path(path)
    logger.debug("load_umtc_input path=%s", resolved)
    payload = _read_json(resolved)
    _validate_or_raise(payload, "umtc_input.schema.json")
    logger.debug("load_umtc_input.ok path=%s", resolved)
    return payload


def write_umtc_output(path: str | pathlib.Path, payload: JsonDict) -> None:
    """Validate and write an ``ac-umtc`` output document."""

    logger.debug("write_umtc_output path=%s", path)
    _validate_or_raise(payload, "umtc_output.schema.json")
    resolved = _to_path(path)
    _write_json(resolved, payload)
    logger.debug("write_umtc_output.ok path=%s", resolved)


__all__ = [
    "load_mfusion_input",
    "load_umtc_input",
    "write_umtc_output",
]
