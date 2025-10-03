import json
import pathlib

import pytest
from jsonschema import Draft202012Validator
from jsonschema import exceptions as js_ex

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCH = ROOT / "schemas"
EX = ROOT / "tests" / "examples"


def _load(name: str):
    return json.loads((EX / name).read_text(encoding="utf-8"))


def _sch(name: str):
    return json.loads((SCH / name).read_text(encoding="utf-8"))


def _assert_valid(schema_name: str, example_name: str) -> None:
    sch = _sch(schema_name)
    doc = _load(example_name)
    Draft202012Validator(sch).validate(doc)


def _assert_invalid(schema_name: str, example_name: str) -> None:
    sch = _sch(schema_name)
    doc = _load(example_name)
    with pytest.raises(js_ex.ValidationError):
        Draft202012Validator(sch).validate(doc)


# --- mfusion ---


def test_mfusion_good_vecz2_passes() -> None:
    _assert_valid("mfusion_input.schema.json", "Vec_Z2_mfusion.json")


def test_mfusion_good_rep_d8_passes() -> None:
    _assert_valid("mfusion_input.schema.json", "rep_d8_mfusion.json")


def test_mfusion_bad_key_fails() -> None:
    _assert_invalid("mfusion_input.schema.json", "bad_mfusion_bad_key.json")


def test_mfusion_missing_dual_fails() -> None:
    _assert_invalid("mfusion_input.schema.json", "bad_mfusion_missing_dual.json")


# --- umtc input ---


def test_umtc_input_toric_min_passes() -> None:
    _assert_valid("umtc_input.schema.json", "toric_umtc_input.min.json")


def test_umtc_input_ising_min_passes() -> None:
    _assert_valid("umtc_input.schema.json", "ising_umtc_input.min.json")


# --- umtc output ---


def test_umtc_output_min_passes() -> None:
    _assert_valid("umtc_output.schema.json", "umtc_output.min.json")


def test_umtc_output_missing_provenance_fails() -> None:
    _assert_invalid(
        "umtc_output.schema.json", "bad_umtc_output_missing_provenance.json"
    )


def test_umtc_output_extra_topkey_fails() -> None:
    _assert_invalid("umtc_output.schema.json", "bad_umtc_output_extra_topkey.json")
