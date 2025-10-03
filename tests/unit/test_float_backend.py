import math

import pytest

from anyon_condense.core.exceptions import NumericFieldError
from anyon_condense.scalars.float_backend import (
    is_finite,
    is_negative_zero,
    linalg_norm_2,
    normalize_float,
    safe_sum,
)


def test_is_finite_negative_zero_normalize():
    assert is_finite(1.23)
    assert not is_finite(float("inf"))
    assert not is_finite(float("-inf"))
    assert not is_finite(float("nan"))

    assert is_negative_zero(-0.0)
    assert not is_negative_zero(0.0)

    assert normalize_float(-0.0) == 0.0
    assert math.copysign(1.0, normalize_float(-0.0)) == 1.0

    with pytest.raises(NumericFieldError):
        normalize_float(float("nan"))
    with pytest.raises(NumericFieldError):
        normalize_float(float("inf"))


def test_safe_sum_matches_fsum_on_cancellation():
    xs = [1e16, 1.0, -1e16]
    naive = sum(xs)
    compensated = safe_sum(xs)
    reference = math.fsum(xs)

    assert abs(compensated - 1.0) <= 1e-12
    assert abs(compensated - reference) <= 1e-12
    assert math.isclose(naive, reference, rel_tol=0.0, abs_tol=0.0)

    assert safe_sum([0.0, -0.0]) == 0.0
    assert math.copysign(1.0, safe_sum([0.0, -0.0])) == 1.0

    with pytest.raises(NumericFieldError):
        safe_sum([1.0, float("nan")])


def test_linalg_norm_2_scaling_and_zero_behavior():
    big = [1e200, 1e200]
    small = [1e-200, 1e-200]
    zeros = [0.0, -0.0, 0.0]

    nb = linalg_norm_2(big)
    ns = linalg_norm_2(small)
    nz = linalg_norm_2(zeros)

    baseline_big = math.sqrt(2.0) * 1e200
    baseline_small = math.sqrt(2.0) * 1e-200

    assert abs(nb - baseline_big) / baseline_big < 1e-12
    assert abs(ns - baseline_small) / baseline_small < 1e-12
    assert nz == 0.0 and math.copysign(1.0, nz) == 1.0

    with pytest.raises(NumericFieldError):
        linalg_norm_2([1.0, float("inf")])
