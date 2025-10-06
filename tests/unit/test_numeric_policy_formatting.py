from __future__ import annotations

import pytest

from anyon_condense.scalars.numeric_policy import (
    NumericPolicy,
    approx_equal,
    format_float,
)


def test_approx_equal_absolute_vs_relative_tolerance() -> None:
    policy = NumericPolicy(tol_abs=1e-10, tol_rel=1e-10)

    assert approx_equal(0.0, 5e-11, policy) is True
    assert approx_equal(0.0, 2e-10, policy) is False

    tighter = NumericPolicy(tol_abs=1e-12, tol_rel=1e-10)
    assert approx_equal(0.0, 5e-11, tighter) is False


def test_approx_equal_large_values_relative_component() -> None:
    a, b = 1e6, 1e6 + 0.2
    strict = NumericPolicy(tol_abs=1e-12, tol_rel=1e-7)
    loose = NumericPolicy(tol_abs=1e-12, tol_rel=1e-6)

    assert approx_equal(a, b, strict) is False
    assert approx_equal(a, b, loose) is True


def test_approx_equal_negative_zero_symmetry() -> None:
    policy = NumericPolicy()
    assert approx_equal(-0.0, 0.0, policy) is True
    assert approx_equal(1.0, 1.0 + 5e-11, policy) == approx_equal(
        1.0 + 5e-11, 1.0, policy
    )


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (0.0, 0.0, True),
        (1e-8, 2e-8, False),  # way beyond tol_abs
        (1e12, 1e12 + 1e5, False),
    ],
)
def test_approx_equal_parameterized_cases(a: float, b: float, expected: bool) -> None:
    policy = NumericPolicy(tol_abs=1e-10, tol_rel=1e-10)
    assert approx_equal(a, b, policy) is expected


def test_format_fixed_round_half_even_and_away() -> None:
    value_pos = 1.25  # exact tie in binary/decimal
    value_neg = -1.25

    even = NumericPolicy(fmt="fixed", precision=1, round_half="even")
    away = NumericPolicy(fmt="fixed", precision=1, round_half="away")

    assert format_float(value_pos, even) == "1.2"
    assert format_float(value_pos, away) == "1.3"
    assert format_float(value_neg, even) == "-1.2"
    assert format_float(value_neg, away) == "-1.3"


def test_format_scientific_precision() -> None:
    policy = NumericPolicy(fmt="scientific", precision=3)
    output = format_float(123456.0, policy)
    assert "e" in output.lower()


def test_format_auto_switches_modes() -> None:
    policy = NumericPolicy(fmt="auto", precision=6)
    tiny = format_float(1e-9, policy)
    mid = format_float(12.3456789, policy)

    assert tiny == "0" or "e" in tiny.lower()
    assert "e" not in mid.lower()


def test_format_negative_zero_unified() -> None:
    policy = NumericPolicy(fmt="fixed", precision=3)
    neg0 = format_float(-0.0, policy)
    pos0 = format_float(0.0, policy)

    assert neg0 == pos0
    assert float(neg0) == 0.0


def test_format_fixed_rounding_boundary_negative() -> None:
    even = NumericPolicy(fmt="fixed", precision=1, round_half="even")
    away = NumericPolicy(fmt="fixed", precision=1, round_half="away")

    assert format_float(-1.25, even) == "-1.2"
    assert format_float(-1.25, away) == "-1.3"


def test_format_scientific_handles_small_numbers() -> None:
    policy = NumericPolicy(fmt="scientific", precision=4)
    out = format_float(3.21e-9, policy)
    assert "e" in out.lower()


def test_auto_respects_clip_small() -> None:
    with_clip = NumericPolicy(fmt="auto", precision=4, clip_small=True)
    without_clip = NumericPolicy(fmt="auto", precision=4, clip_small=False)

    assert format_float(5e-8, with_clip) == "0"
    assert format_float(5e-8, without_clip) != "0"
