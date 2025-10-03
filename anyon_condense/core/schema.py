"""Schema loading, caching, and validation helpers."""

from __future__ import annotations

import json
import os
import pathlib
from typing import Any, Dict, Optional

from jsonschema import Draft202012Validator
from jsonschema import exceptions as js_ex

from .exceptions import SchemaError
from .logging import get_logger

# Internal caches keyed by fully-resolved schema directory + filename.
_SCHEMA_CACHE: Dict[str, dict[str, Any]] = {}
_VALIDATOR_CACHE: Dict[str, Draft202012Validator] = {}

logger = get_logger(__name__)


def get_default_schema_dir() -> pathlib.Path:
    """Return the repository's default schema directory."""

    return pathlib.Path(__file__).resolve().parents[2] / "schemas"


def resolve_schema_dir(override: Optional[str | pathlib.Path] = None) -> pathlib.Path:
    """Resolve the active schema directory."""

    if override:
        path = pathlib.Path(override).expanduser().resolve()
        if not path.is_dir():
            logger.error("[ACIO01] read_error (schema_dir_missing) path=%s", path)
            raise SchemaError(f"Schema dir override not found: {path}")
        logger.debug("schema_dir_resolved path=%s", path)
        return path

    env_override = os.environ.get("AC_SCHEMA_DIR")
    if env_override:
        path = pathlib.Path(env_override).expanduser().resolve()
        if not path.is_dir():
            logger.error("[ACIO01] read_error (schema_dir_missing) path=%s", path)
            raise SchemaError(f"AC_SCHEMA_DIR does not exist: {path}")
        logger.debug("schema_dir_resolved path=%s", path)
        return path

    path = get_default_schema_dir()
    logger.debug("schema_dir_resolved path=%s", path)
    return path


def _schema_path_by_name(
    name: str, schema_dir: Optional[str | pathlib.Path] = None
) -> pathlib.Path:
    """Return the path to *name* inside *schema_dir* (or resolved default)."""

    if not name.endswith(".schema.json"):
        raise SchemaError("Schema name must end with '.schema.json'!")

    base = resolve_schema_dir(schema_dir)
    path = (base / name).resolve()
    if not path.is_file():
        logger.error("[ACIO01] read_error (schema_file_missing) path=%s", path)
        raise SchemaError(f"Schema file not found: {path}")
    return path


def _cache_key(name: str, schema_dir: Optional[str | pathlib.Path]) -> str:
    directory = resolve_schema_dir(schema_dir)
    return f"{directory}::{name}"


def list_schemas(schema_dir: Optional[str | pathlib.Path] = None) -> list[str]:
    """Return a sorted list of available schema filenames."""

    directory = resolve_schema_dir(schema_dir)
    return sorted(f.name for f in directory.glob("*.schema.json") if f.is_file())


def load_schema(
    name: str, schema_dir: Optional[str | pathlib.Path] = None
) -> dict[str, Any]:
    """Load a JSON schema and cache the parsed result."""

    key = _cache_key(name, schema_dir)
    if key in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[key]

    path = _schema_path_by_name(name, schema_dir)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("[ACIO01] read_error name=%s exc=%s", name, exc.__class__.__name__)
        raise SchemaError(f"Failed to read schema '{name}': {exc}") from exc

    if not isinstance(payload, dict) or "$schema" not in payload:
        raise SchemaError(f"Invalid schema (missing $schema): {path}")

    _SCHEMA_CACHE[key] = payload
    return payload


def _get_validator(
    name: str, schema_dir: Optional[str | pathlib.Path] = None
) -> Draft202012Validator:
    """Return a cached Draft202012 validator for *name*."""

    key = _cache_key(name, schema_dir)
    if key in _VALIDATOR_CACHE:
        return _VALIDATOR_CACHE[key]

    schema = load_schema(name, schema_dir)
    try:
        validator = Draft202012Validator(schema)
    except Exception as exc:  # pragma: no cover - defensive
        raise SchemaError(f"Failed to build validator for '{name}': {exc}") from exc

    _VALIDATOR_CACHE[key] = validator
    return validator


def validate(
    payload: dict[str, Any],
    schema_name: str,
    schema_dir: Optional[str | pathlib.Path] = None,
) -> None:
    """Validate *payload* against *schema_name*."""

    validator = _get_validator(schema_name, schema_dir)
    try:
        validator.validate(payload)
    except js_ex.ValidationError as exc:
        location = " → ".join(str(part) for part in exc.path) or "(root)"
        schema_path = _schema_path_by_name(schema_name, schema_dir)
        msg = (
            f"Schema validation error in '{schema_name}' at {location} "
            f"(schema={schema_path}): {exc.message}"
        )
        logger.error(
            "[ACVAL01] schema_validation_error schema=%s loc=%s msg=%s",
            schema_name,
            location,
            exc.message,
        )
        raise SchemaError(msg) from exc


def clear_caches() -> None:
    """Clear cached schema payloads and validators (useful for tests)."""

    _SCHEMA_CACHE.clear()
    _VALIDATOR_CACHE.clear()
