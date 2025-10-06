from __future__ import annotations

from typing import Any, Dict

from anyon_condense.core.hashing import sha256_of_payload_normalized
from anyon_condense.core.numdump import normalized_canonical_dump
from anyon_condense.scalars.numeric_policy import NumericPolicy


def test_same_semantics_different_repr_dump_equal_and_hash_equal() -> None:
    payload_a: Dict[str, Any] = {
        "a": 1.0,
        "b": [0.000000000001, 1.23456789, -0.0],
    }
    payload_b: Dict[str, Any] = {
        "a": 1.0,
        "b": [1e-12, 1.23456789, -0.0],
    }

    policy = NumericPolicy(fmt="auto", precision=12)

    dump_a = normalized_canonical_dump(payload_a, policy)
    dump_b = normalized_canonical_dump(payload_b, policy)
    assert dump_a == dump_b

    hash_a = sha256_of_payload_normalized(payload_a, policy)
    hash_b = sha256_of_payload_normalized(payload_b, policy)
    assert hash_a == hash_b


def test_array_reorder_true_sorts_pure_scalar_flat_array() -> None:
    payload = {"arr": [3.0, 1.0, 2.0, 0.0, -0.0]}
    payload_sorted = {"arr": [0.0, 0.0, 1.0, 2.0, 3.0]}

    policy_sort = NumericPolicy(fmt="auto", precision=8, array_reorder=True)
    policy_keep = NumericPolicy(fmt="auto", precision=8, array_reorder=False)

    dump_sorted = normalized_canonical_dump(payload, policy_sort)
    dump_expected = normalized_canonical_dump(payload_sorted, policy_sort)
    dump_keep = normalized_canonical_dump(payload, policy_keep)

    assert dump_sorted == dump_expected
    assert dump_sorted != dump_keep


def test_array_reorder_true_does_not_reorder_mixed_or_nested() -> None:
    mixed = {"arr": [1.0, "x", 2.0, 0.0]}
    mixed_reordered = {"arr": [0.0, 1.0, 2.0, "x"]}

    nested = {"arr": [[2.0], [1.0]]}
    nested_reordered = {"arr": [[1.0], [2.0]]}

    policy = NumericPolicy(fmt="auto", precision=8, array_reorder=True)

    dump_mixed = normalized_canonical_dump(mixed, policy)
    dump_mixed_reordered = normalized_canonical_dump(mixed_reordered, policy)
    dump_nested = normalized_canonical_dump(nested, policy)
    dump_nested_reordered = normalized_canonical_dump(nested_reordered, policy)

    assert dump_mixed != dump_mixed_reordered
    assert dump_nested != dump_nested_reordered
