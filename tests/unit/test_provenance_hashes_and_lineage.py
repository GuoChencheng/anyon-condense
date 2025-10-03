import json
import math
import pathlib

import pytest

from anyon_condense.core.exceptions import DataIOError
from anyon_condense.core.io import write_umtc_output
from anyon_condense.core.provenance import append_sources_inplace

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT / "tests" / "examples"


def _payload_without_prov_and_hash():
    payload = json.loads(
        (EXAMPLES_DIR / "umtc_output.min.json").read_text(encoding="utf-8")
    )
    payload.pop("provenance", None)
    payload.pop("hashes", None)
    payload["_sources"] = [str(EXAMPLES_DIR / "toric_umtc_input.min.json")]
    return payload


def test_hashes_attached_and_stable(tmp_path: pathlib.Path) -> None:
    out1 = tmp_path / "out1.json"
    out2 = tmp_path / "out2.json"

    payload1 = _payload_without_prov_and_hash()
    write_umtc_output(out1, payload1)
    hashes1 = json.loads(out1.read_text(encoding="utf-8"))["hashes"]

    payload2 = _payload_without_prov_and_hash()
    write_umtc_output(out2, payload2)
    hashes2 = json.loads(out2.read_text(encoding="utf-8"))["hashes"]

    assert set(hashes1.keys()) >= {"objects", "qdim", "global_dim", "twist", "S", "T"}
    assert hashes1 == hashes2


def test_hashes_change_when_subfield_changes(tmp_path: pathlib.Path) -> None:
    out_path = tmp_path / "out.json"
    payload = _payload_without_prov_and_hash()
    payload["twist"]["em"] = 1.0

    write_umtc_output(out_path, payload)
    hashes = json.loads(out_path.read_text(encoding="utf-8"))["hashes"]

    assert "twist" in hashes
    assert hashes["twist"].startswith("sha256:")


def test_append_sources_merges_and_dedups(tmp_path: pathlib.Path) -> None:
    out_path = tmp_path / "out.json"
    payload = _payload_without_prov_and_hash()
    write_umtc_output(out_path, payload)

    saved = json.loads(out_path.read_text(encoding="utf-8"))
    append_sources_inplace(
        saved,
        [
            str(EXAMPLES_DIR / "toric_umtc_input.min.json"),
            "umtc:sha256:abcdef",
        ],
    )

    out_path2 = tmp_path / "out2.json"
    write_umtc_output(out_path2, saved)

    saved2 = json.loads(out_path2.read_text(encoding="utf-8"))
    sources = saved2["provenance"]["sources"]

    assert sources[0].endswith("toric_umtc_input.min.json")
    assert "umtc:sha256:abcdef" in sources


def test_hash_error_on_nan_bubbles_as_dataioerror(tmp_path: pathlib.Path) -> None:
    out_bad = tmp_path / "out_bad.json"
    payload = _payload_without_prov_and_hash()
    payload["S"] = [[math.nan]]

    with pytest.raises(DataIOError):
        write_umtc_output(out_bad, payload)
