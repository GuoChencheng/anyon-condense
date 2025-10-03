#!/usr/bin/env python3
import json
import pathlib

from jsonschema import Draft202012Validator
from jsonschema import exceptions as js_ex

root = pathlib.Path(__file__).resolve().parents[1]
sch_dir = root / "schemas"
ex_dir = root / "tests" / "examples"

# 明确列出所有要校验的 (schema, example, expect_fail)
CASES = [
    # --- mfusion good ---
    ("mfusion_input.schema.json", "Vec_Z2_mfusion.json", False),
    ("mfusion_input.schema.json", "rep_d8_mfusion.json", False),
    # --- mfusion bad ---
    ("mfusion_input.schema.json", "bad_mfusion_missing_dual.json", True),
    ("mfusion_input.schema.json", "bad_mfusion_bad_key.json", True),
    # --- umtc input good ---
    ("umtc_input.schema.json", "toric_umtc_input.min.json", False),
    ("umtc_input.schema.json", "ising_umtc_input.min.json", False),
    # --- umtc output good ---
    ("umtc_output.schema.json", "umtc_output.min.json", False),
    # --- umtc output bad ---
    ("umtc_output.schema.json", "bad_umtc_output_missing_provenance.json", True),
    ("umtc_output.schema.json", "bad_umtc_output_extra_topkey.json", True),
]


def load_json(p: pathlib.Path):
    return json.loads(p.read_text())


def validate_one(schema_name: str, example_name: str, expect_fail: bool) -> bool:
    sch = load_json(sch_dir / schema_name)
    doc = load_json(ex_dir / example_name)
    try:
        Draft202012Validator(sch).validate(doc)
        if expect_fail:
            print(f"UNEXPECTED PASS  {example_name}  against  {schema_name}")
            return False
        else:
            print(f"OK               {example_name}  against  {schema_name}")
            return True
    except js_ex.ValidationError as err:
        if expect_fail:
            print(
                f"EXPECTED FAIL    {example_name}  against  {schema_name}  -> {err.message}"
            )
            return True
        else:
            print(
                f"FAIL             {example_name}  against  {schema_name}  -> {err.message}"
            )
            return False


def main() -> int:
    results = [validate_one(*case) for case in CASES]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
