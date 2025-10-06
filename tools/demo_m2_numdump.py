#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from anyon_condense.core.exceptions import CanonicalizationError, NumericFieldError
from anyon_condense.core.hashing import sha256_of_payload
from anyon_condense.core.numdump import normalize_payload_numbers
from anyon_condense.core.utils import canonical_json_dump
from anyon_condense.utils.profiles import get_numeric_policy


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="demo_m2_numdump",
        description=(
            "Normalize a JSON payload using NumericPolicy, show canonical prefixes "
            "before/after, and print the normalized sha256."
        ),
    )
    parser.add_argument(
        "--in", dest="input", required=True, help="Path to input JSON file"
    )
    parser.add_argument(
        "--fmt",
        choices=["auto", "fixed", "scientific"],
        help="Override NumericPolicy.fmt",
    )
    parser.add_argument(
        "--precision", type=int, help="Override NumericPolicy.precision"
    )
    return parser.parse_args(argv)


def _read_json(path: Path) -> object:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        print(f"[demo] File not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as exc:
        print(f"[demo] JSON decode error in {path}: {exc}", file=sys.stderr)
        raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    overrides: dict[str, object] = {}
    if args.fmt is not None:
        overrides["fmt"] = args.fmt
    if args.precision is not None:
        overrides["precision"] = int(args.precision)

    policy = get_numeric_policy(env=os.environ, overrides=overrides or None)

    payload = _read_json(Path(args.input))

    try:
        before = canonical_json_dump(payload)
    except CanonicalizationError as exc:
        print(
            f"[demo] Numeric error (NaN/Inf or invalid value): {exc}",
            file=sys.stderr,
        )
        return 2

    try:
        normalized = normalize_payload_numbers(payload, policy)
        after = canonical_json_dump(normalized)
        digest = sha256_of_payload(normalized)
    except (NumericFieldError, CanonicalizationError) as exc:
        print(
            f"[demo] Numeric error (NaN/Inf or invalid value): {exc}", file=sys.stderr
        )
        return 2
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[demo] Unexpected error: {exc}", file=sys.stderr)
        return 2

    print("POLICY:", canonical_json_dump(policy.snapshot()))
    print("BEFORE:", before[:120])
    print("AFTER :", after[:120])
    print("EQUAL :", "YES" if before == after else "NO")
    print("SHA256(normalized):", digest)
    return 0


if __name__ == "__main__":  # pragma: no cover - script entrypoint
    raise SystemExit(main())
