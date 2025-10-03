import json
import pathlib

import pytest

from anyon_condense.core import schema as sc
from anyon_condense.core.exceptions import SchemaError

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
EXAMPLES_DIR = ROOT / "tests" / "examples"


def test_list_schemas_contains_expected():
    names = sc.list_schemas()
    assert "mfusion_input.schema.json" in names
    assert "umtc_input.schema.json" in names
    assert "umtc_output.schema.json" in names


def test_load_and_cache_schema():
    sc.clear_caches()
    name = "mfusion_input.schema.json"
    first = sc.load_schema(name)
    second = sc.load_schema(name)
    assert first is second


def test_resolve_schema_dir_override_env(tmp_path, monkeypatch):
    monkeypatch.setenv("AC_SCHEMA_DIR", str(tmp_path))
    # Copy schema and tweak title so we can detect override usage
    source = SCHEMA_DIR / "mfusion_input.schema.json"
    target = tmp_path / "mfusion_input.schema.json"
    payload = source.read_text(encoding="utf-8").replace(
        "ac-mfusion input (v0)", "ac-mfusion input (v0) OVERRIDE"
    )
    target.write_text(payload, encoding="utf-8")

    resolved = sc.resolve_schema_dir()
    assert resolved == tmp_path.resolve()

    sc.clear_caches()
    loaded = sc.load_schema("mfusion_input.schema.json")
    assert loaded["title"].endswith("OVERRIDE")


def test_validate_good_and_bad_examples():
    good_doc = json.loads(
        (EXAMPLES_DIR / "Vec_Z2_mfusion.json").read_text(encoding="utf-8")
    )
    sc.validate(good_doc, "mfusion_input.schema.json")

    bad_doc = json.loads(
        (EXAMPLES_DIR / "bad_mfusion_missing_dual.json").read_text(encoding="utf-8")
    )
    with pytest.raises(SchemaError) as excinfo:
        sc.validate(bad_doc, "mfusion_input.schema.json")
    assert "schema validation error" in str(excinfo.value).lower()


def test_schema_name_suffix_guard():
    with pytest.raises(SchemaError):
        sc.load_schema("mfusion_input.json")


def test_schema_file_not_found():
    with pytest.raises(SchemaError):
        sc.load_schema("not_real.schema.json")


def test_validator_cache_persists():
    sc.clear_caches()
    getter = getattr(sc, "_get_validator")
    first = getter("umtc_input.schema.json")
    second = getter("umtc_input.schema.json")
    assert first is second
