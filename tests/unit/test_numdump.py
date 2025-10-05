import math

import pytest

from anyon_condense.core.exceptions import NumericFieldError
from anyon_condense.core.numdump import (
    normalize_payload_numbers,
    normalized_canonical_dump,
)
from anyon_condense.scalars.numeric_policy import NumericPolicy


def test_normalize_numbers_basic_and_negative_zero_unification():
    policy = NumericPolicy(fmt="fixed", precision=3)
    payload = {
        "a": -0.0,
        "b": [1.23456, 1e-7, -0.0],
        "c": {"x": 1.9995, "y": 2.0004},
        "d": 0.0,
        "e": 42,
        "s": "txt",
        "n": None,
    }
    out = normalize_payload_numbers(payload, policy)
    assert out["a"] == 0.0 and math.copysign(1.0, out["a"]) == 1.0
    assert out["b"][0] == 1.235
    assert out["b"][1] == 0.0 and math.copysign(1.0, out["b"][1]) == 1.0
    assert out["b"][2] == 0.0
    assert out["c"]["x"] == 2.0
    assert out["c"]["y"] == 2.0
    assert out["e"] == 42 and out["s"] == "txt" and out["n"] is None


def test_array_reorder_for_flat_numeric_arrays_only():
    policy = NumericPolicy(array_reorder=True, fmt="fixed", precision=2)
    payload = {
        "nums": [0.0, -0.0, 3.1415, -2.5, 1.234],
        "mix": [1.0, True, 0.0],
        "nest": [[1.0, 0.0], 2.0],
    }
    out = normalize_payload_numbers(payload, policy)
    assert out["nums"] == [-2.5, 0.0, 0.0, 1.23, 3.14]
    assert out["mix"] == [1.0, True, 0.0]
    assert out["nest"][0] == [1.0, 0.0] and out["nest"][1] == 2.0


def test_normalized_canonical_dump_stability_across_repr_variants():
    policy = NumericPolicy(fmt="auto", precision=4)
    payload_a = {"v": [0.000000000001, 1.23456789, -0.0]}
    payload_b = {"v": [1e-12, 1.23456789, -0.0]}
    dump_a = normalized_canonical_dump(payload_a, policy)
    dump_b = normalized_canonical_dump(payload_b, policy)
    assert dump_a == dump_b


def test_non_finite_rejection():
    policy = NumericPolicy()
    with pytest.raises(NumericFieldError):
        normalize_payload_numbers({"x": float("nan")}, policy)
    with pytest.raises(NumericFieldError):
        normalize_payload_numbers({"x": float("inf")}, policy)


def test_scientific_precision_path():
    policy = NumericPolicy(fmt="scientific", precision=3, clip_small=False)
    out = normalize_payload_numbers({"x": 1234567.0, "y": -0.000012345}, policy)
    assert out["x"] == pytest.approx(1.23e6, rel=1e-12)
    assert out["y"] == pytest.approx(-1.23e-5, rel=1e-12)
