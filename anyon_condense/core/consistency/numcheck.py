from __future__ import annotations

from typing import Sequence, Union

from anyon_condense.scalars.numeric_policy import NumericPolicy, approx_equal

Number = Union[int, float, complex]

__all__ = [
    "approx_equal_number",
    "approx_equal_vectors",
    "approx_equal_matrices",
    "max_abs_diff",
]


def approx_equal_number(a: Number, b: Number, policy: NumericPolicy) -> bool:
    """Return True when two scalars are approximately equal under the policy."""

    if isinstance(a, complex) or isinstance(b, complex):
        ar, ai = (a.real, a.imag) if isinstance(a, complex) else (float(a), 0.0)
        br, bi = (b.real, b.imag) if isinstance(b, complex) else (float(b), 0.0)
        return approx_equal(ar, br, policy) and approx_equal(ai, bi, policy)
    return approx_equal(float(a), float(b), policy)


def approx_equal_vectors(
    u: Sequence[Number], v: Sequence[Number], policy: NumericPolicy
) -> bool:
    if len(u) != len(v):
        return False
    for x, y in zip(u, v):
        if not approx_equal_number(x, y, policy):
            return False
    return True


def approx_equal_matrices(
    a: Sequence[Sequence[Number]],
    b: Sequence[Sequence[Number]],
    policy: NumericPolicy,
) -> bool:
    if len(a) != len(b):
        return False
    for row_a, row_b in zip(a, b):
        if len(row_a) != len(row_b):
            return False
        for x, y in zip(row_a, row_b):
            if not approx_equal_number(x, y, policy):
                return False
    return True


def max_abs_diff(a: Sequence[Sequence[Number]], b: Sequence[Sequence[Number]]) -> float:
    """Return the maximum absolute elementwise difference between matrices."""

    maximum = 0.0
    for row_a, row_b in zip(a, b):
        for x, y in zip(row_a, row_b):
            diff = abs(x - y)
            if diff > maximum:
                maximum = diff
    return maximum
