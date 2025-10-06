from __future__ import annotations

from typing import Iterable, List

import pytest

from anyon_condense.core.consistency.modular import check_modular_relations
from anyon_condense.scalars.numeric_policy import NumericPolicy


def toric_st() -> tuple[List[List[float]], List[List[float]]]:
    s = [
        [0.5, 0.5, 0.5, 0.5],
        [0.5, 0.5, -0.5, -0.5],
        [0.5, -0.5, 0.5, -0.5],
        [0.5, -0.5, -0.5, 0.5],
    ]
    t = [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, -1.0],
    ]
    return s, t


def inject_noise(
    matrix: Iterable[Iterable[float]], epsilon: float
) -> List[List[float]]:
    result: List[List[float]] = []
    sign = 1.0
    for row in matrix:
        new_row: List[float] = []
        for value in row:
            new_row.append(value + sign * epsilon)
            sign = -sign
        result.append(new_row)
    return result


def assert_policy_snapshot(report: dict, *, tol_abs: float, tol_rel: float) -> None:
    assert "policy_snapshot" in report
    snapshot = report["policy_snapshot"]
    for key in ("fmt", "precision", "tol_abs", "tol_rel"):
        assert key in snapshot
    assert snapshot["tol_abs"] == pytest.approx(tol_abs)
    assert snapshot["tol_rel"] == pytest.approx(tol_rel)


def test_toric_modular_small_noise_passes_default_policy() -> None:
    s, t = toric_st()
    noisy_s = inject_noise(s, 1e-12)

    policy = NumericPolicy(tol_abs=1e-10, tol_rel=1e-10)
    report = check_modular_relations(noisy_s, t, policy)

    assert report["status"] is True
    metrics = report["metrics"]
    assert metrics["max_err_st3_s2"] >= 0.0
    assert "max_err_s4_i" in metrics
    assert_policy_snapshot(report, tol_abs=1e-10, tol_rel=1e-10)


def test_toric_modular_large_noise_behaviour() -> None:
    s, t = toric_st()
    noisy_s = inject_noise(s, 1e-6)

    policy_default = NumericPolicy()
    report_fail = check_modular_relations(noisy_s, t, policy_default)
    assert report_fail["status"] is False
    assert_policy_snapshot(
        report_fail, tol_abs=policy_default.tol_abs, tol_rel=policy_default.tol_rel
    )

    policy_loose = NumericPolicy(tol_abs=1e-5, tol_rel=1e-5)
    report_pass = check_modular_relations(noisy_s, t, policy_loose)
    assert report_pass["status"] is True
    assert_policy_snapshot(
        report_pass, tol_abs=policy_loose.tol_abs, tol_rel=policy_loose.tol_rel
    )
