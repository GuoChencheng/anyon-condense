"""JSON IO helpers for schema-backed documents."""

from __future__ import annotations

import json
from typing import Any

from .schema import validate


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def dump_json(path: str, payload: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def load_and_validate(path: str, schema_name: str) -> dict[str, Any]:
    data = load_json(path)
    validate(data, schema_name)
    return data
