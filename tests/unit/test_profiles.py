import pytest

from anyon_condense.scalars.numeric_policy import NumericPolicy
from anyon_condense.utils.profiles import get_numeric_policy


def test_env_defaults_and_overrides_priority():
    p0 = get_numeric_policy(env={})
    assert isinstance(p0, NumericPolicy)
    assert p0.fmt == "auto"
    assert p0.precision == 12
    assert p0.array_reorder is False

    env = {
        "AC_NUMERIC_FMT": "scientific",
        "AC_NUMERIC_PREC": "8",
        "AC_TOL_ABS": "1e-12",
        "AC_TOL_REL": "1e-9",
        "AC_ARRAY_REORDER": "TrUe",
        "AC_ROUND_HALF": "away",
        "AC_CLIP_SMALL": "0",
    }
    p1 = get_numeric_policy(env=env)
    assert p1.fmt == "scientific"
    assert p1.precision == 8
    assert p1.tol_abs == pytest.approx(1e-12)
    assert p1.tol_rel == pytest.approx(1e-9)
    assert p1.array_reorder is True
    assert p1.round_half == "away"
    assert p1.clip_small is False

    p2 = get_numeric_policy(
        env=env,
        overrides={
            "fmt": "fixed",
            "precision": 5,
            "array_reorder": False,
            "clip_small": True,
        },
    )
    assert p2.fmt == "fixed"
    assert p2.precision == 5
    assert p2.array_reorder is False
    assert p2.tol_abs == pytest.approx(1e-12)
    assert p2.clip_small is True


def test_invalid_values_bubble_up_from_numericpolicy():
    env = {"AC_NUMERIC_FMT": "weird"}
    with pytest.raises(ValueError):
        get_numeric_policy(env=env)


def test_boolean_parser_variants():
    truths = ["1", "true", "YES", "On", "TrUe"]
    for value in truths:
        policy = get_numeric_policy(env={"AC_ARRAY_REORDER": value})
        assert policy.array_reorder is True

    falses = ["0", "false", "no", "off", ""]
    for value in falses:
        policy = get_numeric_policy(env={"AC_ARRAY_REORDER": value})
        assert policy.array_reorder is False
