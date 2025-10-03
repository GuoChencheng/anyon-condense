import json
import pathlib

import pytest

from anyon_condense.core.exceptions import DataIOError, ValidationError
from anyon_condense.core.io import (
    load_mfusion_input,
    load_umtc_input,
    write_umtc_output,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT / "tests" / "examples"


# --- Happy path: load mfusion ---


def test_load_mfusion_vecz2_ok() -> None:
    path = EXAMPLES_DIR / "Vec_Z2_mfusion.json"
    doc = load_mfusion_input(path)
    assert isinstance(doc, dict)
    assert doc["format"] == "ac-mfusion"
    assert doc["category_type"] == "mfusion"
    assert isinstance(doc["simple_objects"], list) and doc["simple_objects"]


# --- Happy path: load umtc input ---


def test_load_umtc_input_toric_min_ok() -> None:
    path = EXAMPLES_DIR / "toric_umtc_input.min.json"
    doc = load_umtc_input(path)
    assert isinstance(doc, dict)
    assert doc["format"] == "ac-umtc"
    assert doc["category_type"] == "umtc"
    assert isinstance(doc["simple_objects"], list) and doc["simple_objects"]


# --- Happy path: write umtc output (auto provenance + hashes) ---


def test_write_umtc_output_min_ok(tmp_path: pathlib.Path) -> None:
    out_path = tmp_path / "out.umtc.json"
    payload = json.loads(
        (EXAMPLES_DIR / "umtc_output.min.json").read_text(encoding="utf-8")
    )
    payload.pop("provenance", None)
    payload.pop("hashes", None)
    payload["_sources"] = [str(EXAMPLES_DIR / "toric_umtc_input.min.json")]

    write_umtc_output(out_path, payload)

    saved = json.loads(out_path.read_text(encoding="utf-8"))
    assert saved["format"] == "ac-umtc"
    assert "provenance" in saved and "hashes" in saved

    prov = saved["provenance"]
    assert isinstance(prov.get("generated_by"), str) and prov["generated_by"]
    assert isinstance(prov.get("date"), str) and prov["date"].endswith("Z")
    assert isinstance(prov.get("sources"), list) and prov["sources"]

    hashes = saved["hashes"]
    required_keys = {"objects", "qdim", "global_dim", "twist", "S", "T"}
    assert required_keys.issubset(hashes.keys())
    assert all(
        isinstance(hashes[key], str) and hashes[key].startswith("sha256:")
        for key in hashes
    )


# --- Sad path: schema validation should fail for bad example ---


def test_load_mfusion_bad_missing_dual_raises_validationerror() -> None:
    path = EXAMPLES_DIR / "bad_mfusion_missing_dual.json"
    with pytest.raises(ValidationError):
        load_mfusion_input(path)


# --- Extra guards ---


def test_load_nonexistent_file_raises_dataioerror(tmp_path: pathlib.Path) -> None:
    with pytest.raises(DataIOError):
        load_umtc_input(tmp_path / "no_such.json")


def test_write_umtc_output_rejects_invalid_json_values(tmp_path: pathlib.Path) -> None:
    bad_payload = {
        "format": "ac-umtc",
        "version": "0.1",
        "encoding": "float",
        "number_field": "cyclotomic(8)",
        "category_type": "umtc",
        "objects": ["1"],
        "qdim": {"1": 1.0},
        "global_dim": 1.0,
        "twist": {"1": 1.0},
        "S": [[float("nan")]],
        "T": [[1.0]],
        "checks": {},
        "hashes": {},
    }

    with pytest.raises(DataIOError):
        write_umtc_output(tmp_path / "out.json", bad_payload)
