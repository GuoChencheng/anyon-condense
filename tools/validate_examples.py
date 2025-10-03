#!/usr/bin/env python3
"""Quick validation of example payloads against bundled schemas."""

from __future__ import annotations

import json
import pathlib

from anyon_condense.core.exceptions import SchemaError
from anyon_condense.core.schema import validate

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "tests" / "examples"

CASES = [
    ("mfusion_input.schema.json", "Vec_Z2_mfusion.json", False),
    ("mfusion_input.schema.json", "rep_d8_mfusion.json", False),
    ("mfusion_input.schema.json", "bad_mfusion_missing_dual.json", True),
    ("mfusion_input.schema.json", "bad_mfusion_bad_key.json", True),
    ("umtc_input.schema.json", "toric_umtc_input.min.json", False),
    ("umtc_input.schema.json", "ising_umtc_input.min.json", False),
    ("umtc_output.schema.json", "umtc_output.min.json", False),
    ("umtc_output.schema.json", "bad_umtc_output_missing_provenance.json", True),
    ("umtc_output.schema.json", "bad_umtc_output_extra_topkey.json", True),
]


def load_json(example_name: str) -> dict:
    return json.loads((EXAMPLES_DIR / example_name).read_text(encoding="utf-8"))


def validate_one(schema_name: str, example_name: str, expect_fail: bool) -> bool:
    payload = load_json(example_name)
    try:
        validate(payload, schema_name)
    except SchemaError as err:
        if expect_fail:
            print(f"EXPECTED FAIL    {example_name}  against  {schema_name}  -> {err}")
            return True
        print(f"FAIL             {example_name}  against  {schema_name}  -> {err}")
        return False

    if expect_fail:
        print(f"UNEXPECTED PASS  {example_name}  against  {schema_name}")
        return False

    print(f"OK               {example_name}  against  {schema_name}")
    return True


def main() -> int:
    results = [validate_one(*case) for case in CASES]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
