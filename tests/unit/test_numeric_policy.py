import math

import pytest

from anyon_condense.core.exceptions import NumericFieldError
from anyon_condense.scalars.numeric_policy import (
    NumericPolicy,
    approx_equal,
    clip_small,
    format_float,
    policy_from_env,
    reorder_scalar_array,
)


def test_policy_snapshot_and_env_overrides():
    policy = NumericPolicy()
    snap = policy.snapshot()
    assert snap["fmt"] == "auto"
    assert snap["precision"] == 12

    env = {
        "AC_NUMERIC_FMT": "scientific",
        "AC_NUMERIC_PREC": "6",
        "AC_TOL_ABS": "1e-12",
        "AC_TOL_REL": "1e-9",
        "AC_ARRAY_REORDER": "true",
        "AC_ROUND_HALF": "away",
        "AC_CLIP_SMALL": "false",
    }

    p_env = policy_from_env(env)
    assert p_env.fmt == "scientific"
    assert p_env.precision == 6
    assert p_env.tol_abs == pytest.approx(1e-12)
    assert p_env.tol_rel == pytest.approx(1e-9)
    assert p_env.array_reorder is True
    assert p_env.round_half == "away"
    assert p_env.clip_small is False

    p_override = policy_from_env(env, overrides={"precision": 9})
    assert p_override.precision == 9


def test_approx_equal_and_negative_zero_behavior():
    p = NumericPolicy(tol_abs=1e-10, tol_rel=1e-10)
    assert approx_equal(1.0, 1.0 + 5e-11, p)
    assert not approx_equal(1.0, 1.0 + 5e-9, p)

    big_a, big_b = 1e12, 1e12 + 1e3
    assert not approx_equal(big_a, big_b, p)
    p_relaxed = NumericPolicy(tol_rel=1e-9)
    assert approx_equal(big_a, big_b, p_relaxed)

    assert approx_equal(-0.0, 0.0, p)
    assert approx_equal(1e-15, 0.0, NumericPolicy(precision=12, clip_small=True))


def test_clip_small_and_nonfinite_rejection():
    p = NumericPolicy(precision=3, clip_small=True)
    assert clip_small(3.5e-5, p) == 0.0
    assert clip_small(2e-4, p) != 0.0

    with pytest.raises(NumericFieldError):
        clip_small(float("nan"), p)


def test_format_float_fixed_scientific_auto():
    p_fixed_even = NumericPolicy(fmt="fixed", precision=3, round_half="even")
    assert format_float(1.23456, p_fixed_even) == "1.235"

    p_fixed_even1 = NumericPolicy(fmt="fixed", precision=1, round_half="even")
    assert format_float(1.25, p_fixed_even1) == "1.2"

    p_fixed_away1 = NumericPolicy(fmt="fixed", precision=1, round_half="away")
    assert format_float(1.25, p_fixed_away1) == "1.3"

    p_sci = NumericPolicy(fmt="scientific", precision=3)
    sci_str = format_float(1234567.0, p_sci)
    assert sci_str.startswith("1.") and "e" in sci_str
    assert format_float(0.0, p_sci) == "0e+0"

    p_auto = NumericPolicy(fmt="auto", precision=4)
    assert format_float(0.001234, p_auto).startswith("0.0012")
    assert format_float(0.0, p_auto) == "0"

    p_auto_no_clip = NumericPolicy(fmt="auto", precision=4, clip_small=False)
    assert "e" in format_float(1e-7, p_auto_no_clip)


def test_reorder_scalar_array_behavior():
    arr = [0.0, -0.0, 3.0, -1.0, 2.0]
    p_keep = NumericPolicy(array_reorder=False)
    keep = reorder_scalar_array(arr, p_keep)
    assert keep[0] == 0.0 and math.copysign(1.0, keep[0]) == 1.0
    assert keep[1] == 0.0 and math.copysign(1.0, keep[1]) == 1.0
    assert keep[2:] == [3.0, -1.0, 2.0]

    p_sort = NumericPolicy(array_reorder=True)
    sorted_arr = reorder_scalar_array(arr, p_sort)
    assert sorted_arr == [-1.0, 0.0, 0.0, 2.0, 3.0]

    mix = [1.0, True, 0.0]
    mix_out = reorder_scalar_array(mix, p_sort)
    assert mix_out == [1.0, True, 0.0]
