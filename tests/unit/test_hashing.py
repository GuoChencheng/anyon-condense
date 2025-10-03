import math

import pytest

from anyon_condense.core.exceptions import HashingError
from anyon_condense.core.hashing import content_address, hash_matrix, sha256_of_payload


def test_sha256_payload_deterministic_and_sorted_keys():
    a = {"b": 2, "a": 1, "c": {"y": 2, "x": 1}, "float": -0.0}
    b = {"c": {"x": 1, "y": 2}, "float": -0.0, "a": 1, "b": 2}
    ha = sha256_of_payload(a)
    hb = sha256_of_payload(b)
    assert ha == hb
    assert ha.startswith("sha256:")


def test_sha256_payload_changes_on_value_change():
    assert sha256_of_payload({"a": 1}) != sha256_of_payload({"a": 2})


def test_hash_matrix_basic_and_negative_zero_normalization():
    m1 = [[1.0, -0.0], [2, "x"]]
    m2 = [[1.0, 0.0], [2, "x"]]
    h1 = hash_matrix(m1)
    h2 = hash_matrix(m2)
    assert h1 == h2
    assert h1.startswith("sha256:")


def test_hash_matrix_rejects_bad_types_and_nan():
    with pytest.raises(HashingError):
        hash_matrix(123)  # type: ignore[arg-type]
    with pytest.raises(HashingError):
        hash_matrix([[object()]])
    with pytest.raises(HashingError):
        hash_matrix([[math.nan]])


def test_content_address_variants_and_prefix():
    h1 = content_address({"a": 1}, kind="umtc")
    h2 = content_address({"a": 1}, kind="umtc")
    assert h1 == h2
    assert h1.startswith("umtc:sha256:")

    h3 = content_address({"a": 1}, kind="mfusion")
    assert h3 != h1
    assert h3.split(":", 2)[2] == h1.split(":", 2)[2]

    assert content_address([3, 2, 1], "blob").startswith("blob:sha256:")
    assert content_address("hello", "text").startswith("text:sha256:")
    assert content_address(b"hello", "bytes").startswith("bytes:sha256:")


def test_content_address_unsupported_type():
    class X: ...

    with pytest.raises(HashingError):
        content_address(X(), "custom")
