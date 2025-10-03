import json

import pytest

from anyon_condense.core.exceptions import CanonicalizationError
from anyon_condense.core.utils import canonical_json_dump


def test_sorted_keys_are_equal():
    a = {"b": 2, "a": 1, "c": {"y": 2, "x": 1}}
    b = {"c": {"x": 1, "y": 2}, "a": 1, "b": 2}
    sa = canonical_json_dump(a)
    sb = canonical_json_dump(b)
    assert sa == sb
    assert sa.startswith('{"a":')


def test_utf8_unescaped():
    payload = {"msg": "μ-anyons ✓", "汉字": "测试"}
    dumped = canonical_json_dump(payload)
    assert "μ" in dumped and "汉字" in dumped
    assert "\\u" not in dumped


def test_no_spaces_and_single_line():
    payload = {"k": [1, 2, 3], "x": {"y": True, "z": None}}
    dumped = canonical_json_dump(payload)
    assert " " not in dumped
    assert "\n" not in dumped


def test_negative_zero_normalized():
    payload = {"x": -0.0, "z": 0.0}
    dumped = canonical_json_dump(payload)
    assert "-0.0" not in dumped
    parsed = json.loads(dumped)
    assert parsed["x"] == 0.0 and parsed["z"] == 0.0


def test_reject_nan_inf():
    with pytest.raises(CanonicalizationError):
        canonical_json_dump({"x": float("nan")})
    with pytest.raises(CanonicalizationError):
        canonical_json_dump({"x": float("inf")})


def test_array_reorder_option():
    payload = {"arr": [2, 1, 3]}
    default = canonical_json_dump(payload, reorder_arrays=False)
    reordered = canonical_json_dump(payload, reorder_arrays=True)
    assert default != reordered
    assert json.loads(reordered)["arr"] == [1, 2, 3]


def test_array_reorder_ignores_non_scalar():
    payload = {"arr": [3, {"a": 1}, 2]}
    first = canonical_json_dump(payload, reorder_arrays=True)
    second = canonical_json_dump(payload, reorder_arrays=True)
    assert first == second
    assert json.loads(first)["arr"] == [3, {"a": 1}, 2]


def test_reject_non_string_keys():
    with pytest.raises(CanonicalizationError):
        canonical_json_dump({1: "x"})


def test_top_level_must_be_object():
    with pytest.raises(CanonicalizationError):
        canonical_json_dump(["x", "y"])  # type: ignore[arg-type]
