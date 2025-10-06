from __future__ import annotations

from typing import Any, Dict, List, Sequence, Union

from anyon_condense.core.consistency.numcheck import (
    approx_equal_matrices,
    max_abs_diff,
)
from anyon_condense.scalars.numeric_policy import NumericPolicy

from .report import Report

Number = Union[int, float, complex]


def _eye(n: int) -> List[List[complex]]:
    return [[1.0 + 0.0j if i == j else 0.0 + 0.0j for j in range(n)] for i in range(n)]


def _matmul(
    a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]
) -> List[List[complex]]:
    rows, inner, cols = len(a), len(a[0]), len(b[0])
    result = [[0.0 + 0.0j for _ in range(cols)] for __ in range(rows)]
    for i in range(rows):
        for k in range(inner):
            aik = a[i][k]
            if aik == 0:
                continue
            for j in range(cols):
                result[i][j] += aik * b[k][j]
    return result


def _matpow(a: Sequence[Sequence[complex]], power: int) -> List[List[complex]]:
    if power == 0:
        return _eye(len(a))
    acc: List[List[complex]] = _eye(len(a))
    base: List[List[complex]] = [list(row) for row in a]
    exp = power
    while exp > 0:
        if exp & 1:
            acc = _matmul(acc, base)
        base = _matmul(base, base)
        exp >>= 1
    return acc


def check_modular_relations(
    s_matrix: Sequence[Sequence[Number]],
    t_matrix: Sequence[Sequence[Number]],
    policy: NumericPolicy,
) -> Dict[str, Any]:
    """Check modular identities using approximate comparisons."""

    s_complex = [[complex(entry) for entry in row] for row in s_matrix]
    t_complex = [[complex(entry) for entry in row] for row in t_matrix]

    identity = _eye(len(s_complex))
    st = _matmul(s_complex, t_complex)
    st_cubed = _matpow(st, 3)
    s_squared = _matpow(s_complex, 2)
    s_fourth = _matpow(s_complex, 4)

    ok_st3_eq_s2 = approx_equal_matrices(st_cubed, s_squared, policy)
    ok_s4_eq_i = approx_equal_matrices(s_fourth, identity, policy)

    metrics = {
        "max_err_st3_s2": max_abs_diff(st_cubed, s_squared),
        "max_err_s4_i": max_abs_diff(s_fourth, identity),
    }

    report = Report.from_policy(
        status=bool(ok_st3_eq_s2 and ok_s4_eq_i),
        metrics=metrics,
        policy=policy,
    )
    return report.to_dict()
