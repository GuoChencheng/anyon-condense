from __future__ import annotations

import math

import pytest

from anyon_condense.core.exceptions import NumericFieldError
from anyon_condense.core.hashing import (
    sha256_of_payload,
    sha256_of_payload_normalized,
)
from anyon_condense.scalars.numeric_policy import NumericPolicy


def test_normalized_hash_equal_for_same_semantics() -> None:
    payload_a = {"v": [0.000000000001, 1.23456789, -0.0]}
    payload_b = {"v": [1e-12, 1.23456789, -0.0]}
    policy = NumericPolicy(fmt="auto", precision=4)

    hash_a = sha256_of_payload_normalized(payload_a, policy)
    hash_b = sha256_of_payload_normalized(payload_b, policy)
    assert hash_a == hash_b


def test_raw_hash_may_differ_but_normalized_same() -> None:
    payload_a = {"v": [0.000000000001]}
    payload_b = {"v": [1e-12]}

    raw_a = sha256_of_payload(payload_a)
    raw_b = sha256_of_payload(payload_b)

    policy = NumericPolicy(fmt="auto", precision=6)
    norm_a = sha256_of_payload_normalized(payload_a, policy)
    norm_b = sha256_of_payload_normalized(payload_b, policy)

    assert isinstance(raw_a, str) and isinstance(raw_b, str)
    assert norm_a == norm_b


def test_normalized_hash_differs_for_different_values() -> None:
    policy = NumericPolicy(fmt="fixed", precision=3)
    payload_x = {"x": 1.2344}
    payload_y = {"x": 1.2346}

    hash_x = sha256_of_payload_normalized(payload_x, policy)
    hash_y = sha256_of_payload_normalized(payload_y, policy)
    assert hash_x != hash_y


def test_reject_non_finite_in_normalized_path() -> None:
    policy = NumericPolicy()
    with pytest.raises(NumericFieldError):
        sha256_of_payload_normalized({"x": math.nan}, policy)
