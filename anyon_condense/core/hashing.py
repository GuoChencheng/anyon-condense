"""Stable hashing utilities built on canonical JSON serialization."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, Sequence, Union

from .exceptions import CanonicalizationError, HashingError
from .utils import canonical_json_dump

Number = Union[int, float]
MatrixElem = Union[Number, str]
Matrix = Sequence[Sequence[MatrixElem]]

_SHA_PREFIX = "sha256:"


def _sha256_bytes(data: bytes) -> str:
    return _SHA_PREFIX + hashlib.sha256(data).hexdigest()


def hash_json_value(value: Any) -> str:
    """Return ``sha256:<hex>`` for any JSON-compatible ``value``."""

    try:
        serialized = canonical_json_dump({"_": value})
    except CanonicalizationError as exc:
        raise HashingError(f"Canonicalization failed for value: {exc}") from exc
    return _sha256_bytes(serialized.encode("utf-8"))


def sha256_of_payload(payload: Dict[str, Any]) -> str:
    """Return `sha256:<hex>` for a JSON-compatible dict payload."""

    if not isinstance(payload, dict):
        raise HashingError("sha256_of_payload expects a dict at top level.")
    try:
        serialized = canonical_json_dump(payload)
    except CanonicalizationError as exc:
        raise HashingError(f"Canonicalization failed: {exc}") from exc
    return _sha256_bytes(serialized.encode("utf-8"))


def hash_matrix(matrix: Matrix) -> str:
    """Hash a numeric/string matrix (list[list[number|string]])."""

    if not isinstance(matrix, (list, tuple)):
        raise HashingError("Matrix must be a list/tuple of rows.")
    normalized_rows: list[list[MatrixElem]] = []
    for row in matrix:
        if not isinstance(row, (list, tuple)):
            raise HashingError("Each matrix row must be a list/tuple.")
        normalized_row: list[MatrixElem] = []
        for value in row:
            if not isinstance(value, (int, float, str)):
                raise HashingError(
                    f"Unsupported matrix element type: {type(value).__name__}"
                )
            normalized_row.append(value)
        normalized_rows.append(normalized_row)

    try:
        serialized = canonical_json_dump({"matrix": normalized_rows})
    except CanonicalizationError as exc:
        raise HashingError(f"Matrix canonicalization failed: {exc}") from exc
    return _sha256_bytes(serialized.encode("utf-8"))


def content_address(obj: Any, kind: str) -> str:
    """Return `<kind>:sha256:<hex>` for arbitrary JSON-compatible content."""

    safe_kind = (kind or "blob").replace(":", "-")

    if isinstance(obj, bytes):
        return f"{safe_kind}:{_sha256_bytes(obj)}"
    if isinstance(obj, str):
        return f"{safe_kind}:{_sha256_bytes(obj.encode('utf-8'))}"

    if isinstance(obj, dict):
        wrapper = obj
    elif isinstance(obj, (list, tuple)):
        wrapper = {"_": list(obj)}
    elif obj is None or isinstance(obj, (bool, int, float)):
        wrapper = {"_": obj}
    else:
        raise HashingError(
            f"Unsupported object type for content_address: {type(obj).__name__}"
        )

    try:
        serialized = canonical_json_dump(wrapper)
    except CanonicalizationError as exc:
        raise HashingError(
            f"Canonicalization failed in content_address: {exc}"
        ) from exc
    return f"{safe_kind}:{_sha256_bytes(serialized.encode('utf-8'))}"


def attach_hashes_inplace(payload: dict, fields: Sequence[str] | None = None) -> dict:
    """Ensure ``payload['hashes']`` contains hashes for key substructures."""

    keys = (
        list(fields)
        if fields is not None
        else [
            "objects",
            "qdim",
            "global_dim",
            "twist",
            "S",
            "T",
        ]
    )

    hashes = payload.get("hashes")
    if not isinstance(hashes, dict):
        hashes = {}
        payload["hashes"] = hashes

    for key in keys:
        if key not in payload or key in hashes:
            continue
        hashes[key] = hash_json_value(payload[key])

    return hashes


__all__ = [
    "sha256_of_payload",
    "hash_matrix",
    "content_address",
    "hash_json_value",
    "attach_hashes_inplace",
]
