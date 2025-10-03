import json
import pathlib

import pytest
from jsonschema import Draft202012Validator, exceptions

ROOT = pathlib.Path(__file__).resolve().parents[2]
S = ROOT / "schemas"
E = ROOT / "tests" / "examples"


def load(p):
    return json.loads(pathlib.Path(p).read_text())


def v(sch, doc):
    Draft202012Validator(load(S / sch)).validate(load(E / doc))


def test_mfusion_good_passes():
    v("mfusion_input.schema.json", "Vec_Z2_mfusion.json")


def test_umtc_input_good_passes():
    v("umtc_input.schema.json", "toric_umtc_input.min.json")


def test_mfusion_bad_fails():
    with pytest.raises(exceptions.ValidationError):
        v("mfusion_input.schema.json", "bad_mfusion_missing_dual.json")


def test_top_level_no_extra_keys():
    # 构造一个多余顶层键的文档，应该被拒
    doc = load(E / "Vec_Z2_mfusion.json")
    doc["typo_extra_key"] = 1
    with pytest.raises(exceptions.ValidationError):
        Draft202012Validator(load(S / "mfusion_input.schema.json")).validate(doc)
