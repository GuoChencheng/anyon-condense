import json
import pathlib

from anyon_condense.core.io import write_umtc_output

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT / "tests" / "examples"


def _load_payload_without_provenance():
    payload = json.loads(
        (EXAMPLES_DIR / "umtc_output.min.json").read_text(encoding="utf-8")
    )
    payload.pop("provenance", None)
    payload["_sources"] = [str(EXAMPLES_DIR / "toric_umtc_input.min.json")]
    return payload


def test_write_injects_minimal_provenance(tmp_path: pathlib.Path) -> None:
    out_path = tmp_path / "umtc_out.json"
    payload = _load_payload_without_provenance()
    write_umtc_output(out_path, payload)

    saved = json.loads(out_path.read_text(encoding="utf-8"))
    assert "provenance" in saved
    prov = saved["provenance"]

    assert isinstance(prov.get("generated_by"), str) and prov["generated_by"]
    assert isinstance(prov.get("date"), str) and prov["date"].endswith("Z")
    assert "T" in prov["date"]
    assert isinstance(prov.get("toolchain_version"), str) and prov["toolchain_version"]
    assert "exact_backend_id" in prov and prov["exact_backend_id"] is None
    assert "numeric_policy" in prov and prov["numeric_policy"] is None
    assert isinstance(prov.get("sources"), list) and prov["sources"]
    assert str(EXAMPLES_DIR / "toric_umtc_input.min.json") in prov["sources"]


def test_temp_sources_removed(tmp_path: pathlib.Path) -> None:
    out_path = tmp_path / "out.json"
    payload = _load_payload_without_provenance()
    write_umtc_output(out_path, payload)
    saved = json.loads(out_path.read_text(encoding="utf-8"))
    assert "_sources" not in saved


def test_existing_provenance_respected(tmp_path: pathlib.Path) -> None:
    out_path = tmp_path / "out2.json"
    payload = _load_payload_without_provenance()
    payload["provenance"] = {"generated_by": "ac custom", "sources": ["X"]}
    write_umtc_output(out_path, payload)
    saved = json.loads(out_path.read_text(encoding="utf-8"))
    prov = saved["provenance"]
    assert prov["generated_by"] == "ac custom"
    assert prov["sources"] == ["X"]
    assert "date" in prov and "toolchain_version" in prov
