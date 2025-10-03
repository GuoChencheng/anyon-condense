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


def test_load_mfusion_input_good_vec_z2() -> None:
    doc = load_mfusion_input(EXAMPLES_DIR / "Vec_Z2_mfusion.json")
    assert doc["format"] == "ac-mfusion"
    assert doc["category_type"] == "mfusion"


def test_load_mfusion_input_bad_missing_dual() -> None:
    with pytest.raises(ValidationError):
        load_mfusion_input(EXAMPLES_DIR / "bad_mfusion_missing_dual.json")


def test_load_umtc_input_good_toric_min() -> None:
    doc = load_umtc_input(EXAMPLES_DIR / "toric_umtc_input.min.json")
    assert doc["format"] == "ac-umtc"
    assert doc["category_type"] == "umtc"


def test_load_fails_on_missing_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(DataIOError):
        load_mfusion_input(tmp_path / "nope.json")


def test_load_fails_on_invalid_json(tmp_path: pathlib.Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{ not valid", encoding="utf-8")
    with pytest.raises(DataIOError):
        load_umtc_input(broken)


def test_write_umtc_output_success(tmp_path: pathlib.Path) -> None:
    payload = json.loads(
        (EXAMPLES_DIR / "umtc_output.min.json").read_text(encoding="utf-8")
    )
    out_path = tmp_path / "out.json"
    write_umtc_output(out_path, payload)
    assert out_path.is_file()
    saved = json.loads(out_path.read_text(encoding="utf-8"))
    assert saved["format"] == "ac-umtc"
    assert "provenance" in saved


def test_write_umtc_output_validation_error(tmp_path: pathlib.Path) -> None:
    bad_payload = json.loads(
        (EXAMPLES_DIR / "bad_umtc_output_missing_provenance.json").read_text(
            encoding="utf-8"
        )
    )
    with pytest.raises(ValidationError):
        write_umtc_output(tmp_path / "bad.json", bad_payload)


def test_write_umtc_output_io_error_when_path_is_directory(
    tmp_path: pathlib.Path,
) -> None:
    payload = json.loads(
        (EXAMPLES_DIR / "umtc_output.min.json").read_text(encoding="utf-8")
    )
    target_dir = tmp_path / "as_dir.json"
    target_dir.mkdir()
    with pytest.raises(DataIOError):
        write_umtc_output(target_dir, payload)
