"""Utility helpers including canonical JSON serialization."""

from __future__ import annotations

import json
import math
from typing import Any, Dict, List, Tuple, TypeGuard, Union

from .exceptions import CanonicalizationError

JSONScalar = Union[None, bool, int, float, str]
JSONType = Union[Dict[str, Any], List[Any], JSONScalar]


def _type_rank(value: JSONScalar) -> int:
    if value is None:
        return 0
    if isinstance(value, bool):
        return 1
    if isinstance(value, int) and not isinstance(value, bool):
        return 2
    if isinstance(value, float):
        return 3
    if isinstance(value, str):
        return 4
    return 99


def _is_scalar(value: Any) -> TypeGuard[JSONScalar]:
    return value is None or isinstance(value, (bool, int, float, str))


def _all_scalars(seq: List[JSONType]) -> TypeGuard[List[JSONScalar]]:
    return all(_is_scalar(item) for item in seq)


def _normalize_float(value: float, path: str) -> float:
    if not math.isfinite(value):
        raise CanonicalizationError(f"Non-finite float at {path}: {value}")
    if value == 0.0 and math.copysign(1.0, value) < 0.0:
        return 0.0
    return value


def _normalize_node(node: Any, path: str, *, reorder_arrays: bool) -> JSONType:
    if isinstance(node, dict):
        normalized: Dict[str, Any] = {}
        for key, value in node.items():
            if not isinstance(key, str):
                raise CanonicalizationError(f"Non-string key at {path}: {key!r}")
            child_path = f"{path}.{key}" if path else key
            normalized[key] = _normalize_node(
                value, child_path, reorder_arrays=reorder_arrays
            )
        return normalized

    if isinstance(node, list):
        normalized_items = [
            _normalize_node(value, f"{path}[{index}]", reorder_arrays=reorder_arrays)
            for index, value in enumerate(node)
        ]
        if reorder_arrays and _all_scalars(normalized_items):

            def key_fn(item: JSONScalar) -> Tuple[int, Tuple[Any, ...]]:
                rank = _type_rank(item)
                if isinstance(item, float):
                    return rank, (item,)
                if isinstance(item, (int, bool)) or item is None:
                    return rank, (item,)
                if isinstance(item, str):
                    return rank, (item,)
                return 99, (str(item),)

            normalized_items.sort(key=key_fn)
        return normalized_items

    if node is None or isinstance(node, bool) or isinstance(node, str):
        return node

    if isinstance(node, int) and not isinstance(node, bool):
        return node

    if isinstance(node, float):
        return _normalize_float(node, path)

    raise CanonicalizationError(f"Unsupported type at {path}: {type(node).__name__}")


def canonical_json_dump(
    payload: Dict[str, Any], *, reorder_arrays: bool = False
) -> str:
    if not isinstance(payload, dict):
        raise CanonicalizationError("Top-level must be a JSON object (dict).")

    normalized = _normalize_node(payload, path="$", reorder_arrays=reorder_arrays)

    try:
        return json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except ValueError as exc:  # pragma: no cover
        raise CanonicalizationError(f"JSON serialization error: {exc}") from exc


__all__ = ["canonical_json_dump"]
