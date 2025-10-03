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


def _has_log(caplog, code: str, contains: list[str]) -> bool:
    for record in caplog.records:
        message = record.getMessage()
        if code in message and all(fragment in message for fragment in contains):
            return True
    return False


def test_log_on_missing_file(caplog):
    caplog.set_level("ERROR")
    missing = ROOT / "tests" / "examples" / "no_such.json"
    with pytest.raises(DataIOError):
        load_mfusion_input(missing)
    assert _has_log(caplog, "[ACIO01]", ["read_error", "no_such.json"])


def test_log_on_json_decode_error(tmp_path: pathlib.Path, caplog):
    caplog.set_level("ERROR")
    broken = tmp_path / "broken.json"
    broken.write_text("{not JSON", encoding="utf-8")
    with pytest.raises(DataIOError):
        load_umtc_input(broken)
    assert _has_log(caplog, "[ACIO02]", ["json_decode_error", "broken.json"])


def test_log_on_not_object_error(tmp_path: pathlib.Path, caplog):
    caplog.set_level("ERROR")
    path = tmp_path / "array.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(DataIOError):
        load_umtc_input(path)
    assert _has_log(caplog, "[ACIO03]", ["not_object_error", "array.json"])


def test_log_on_schema_validation_error(caplog):
    caplog.set_level("ERROR")
    with pytest.raises(ValidationError):
        load_mfusion_input(EXAMPLES_DIR / "bad_mfusion_missing_dual.json")
    assert _has_log(
        caplog, "[ACVAL01]", ["schema_validation_error", "mfusion_input.schema.json"]
    )


def test_log_on_write_error(tmp_path: pathlib.Path, caplog):
    caplog.set_level("ERROR")
    payload = json.loads(
        (EXAMPLES_DIR / "umtc_output.min.json").read_text(encoding="utf-8")
    )
    target = tmp_path / "out.json"
    target.mkdir()
    with pytest.raises(DataIOError):
        write_umtc_output(target, payload)
    assert _has_log(caplog, "[ACIO04]", ["write_error", "out.json"])
