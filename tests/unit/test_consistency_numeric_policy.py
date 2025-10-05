from __future__ import annotations

from anyon_condense.core.consistency.hexagon import check_hexagon_equations
from anyon_condense.core.consistency.modular import check_modular_relations
from anyon_condense.core.consistency.numcheck import (
    approx_equal_matrices,
    approx_equal_number,
    max_abs_diff,
)
from anyon_condense.core.consistency.pentagon import check_pentagon_equations
from anyon_condense.scalars.numeric_policy import NumericPolicy


def toric_st():
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


def test_numcheck_scalar_and_matrix():
    policy = NumericPolicy(tol_abs=1e-10, tol_rel=1e-10)
    assert approx_equal_number(1.0, 1.0 + 5e-11, policy)
    assert not approx_equal_number(1.0, 1.0 + 5e-7, policy)

    a = [[1.0, 2.0], [3.0, 4.0]]
    b = [[1.0 + 1e-12, 2.0 - 1e-12], [3.0, 4.0 + 5e-12]]
    assert approx_equal_matrices(a, b, policy)
    assert max_abs_diff(a, b) >= 0.0


def test_modular_relations_noise_sensitivity():
    policy = NumericPolicy(tol_abs=1e-10, tol_rel=1e-10)
    s, t = toric_st()

    report_clean = check_modular_relations(s, t, policy)
    assert report_clean["status"] is True
    assert report_clean["max_err_st3_s2"] <= 1e-12
    assert report_clean["max_err_s4_i"] <= 1e-12

    noisy = [
        [entry + (1e-12 if (i + j) % 2 == 0 else -1e-12) for j, entry in enumerate(row)]
        for i, row in enumerate(s)
    ]
    report_noisy = check_modular_relations(noisy, t, policy)
    assert report_noisy["status"] is True

    coarse = [
        [entry + (1e-6 if (i + j) % 2 == 0 else -1e-6) for j, entry in enumerate(row)]
        for i, row in enumerate(s)
    ]
    report_fail = check_modular_relations(coarse, t, policy)
    assert report_fail["status"] is False

    loose_policy = NumericPolicy(tol_abs=1e-5, tol_rel=1e-5)
    report_pass = check_modular_relations(coarse, t, loose_policy)
    assert report_pass["status"] is True


def test_pentagon_and_hexagon_wrappers():
    policy = NumericPolicy()
    equations = [
        (1.0, 1.0 + 5e-12),
        (2.0, 2.0 - 5e-12),
        (1.0, 1.05),
    ]
    pentagon_report = check_pentagon_equations(equations, policy)
    hexagon_report = check_hexagon_equations(equations, policy)

    assert pentagon_report["status"] is False
    assert pentagon_report["failed"] == 1
    assert pentagon_report["total"] == 3

    assert hexagon_report["status"] is False
    assert hexagon_report["failed"] == 1
    assert hexagon_report["total"] == 3
