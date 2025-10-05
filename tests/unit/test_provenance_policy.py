from __future__ import annotations

import re

import pytest

from anyon_condense.core.provenance import build_provenance
from anyon_condense.scalars.numeric_policy import NumericPolicy


def _is_iso8601_utc(timestamp: str) -> bool:
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\+00:00|Z)$"
    return bool(re.match(pattern, timestamp))


def test_build_provenance_with_policy_object_snapshot() -> None:
    policy = NumericPolicy()
    prov = build_provenance(
        generated_by="ac 0.1.0-dev",
        sources=["tests/examples/Vec_Z2_mfusion.json"],
        exact_backend_id=None,
        numeric_policy=policy,
    )

    assert prov["generated_by"] == "ac 0.1.0-dev"
    assert _is_iso8601_utc(prov["date"])
    assert isinstance(prov["toolchain_version"], str)
    assert prov["exact_backend_id"] is None
    assert prov["sources"] == ["tests/examples/Vec_Z2_mfusion.json"]

    snapshot = prov["numeric_policy"]
    assert snapshot["mode"] == "float"
    assert snapshot["fmt"] == policy.fmt
    assert snapshot["precision"] == policy.precision
    assert snapshot["tol_abs"] == pytest.approx(policy.tol_abs)
    assert snapshot["tol_rel"] == pytest.approx(policy.tol_rel)
    assert "round_half" in snapshot
    assert "array_reorder" in snapshot


def test_build_provenance_with_policy_dict_snapshot() -> None:
    custom_snapshot = {
        "mode": "float",
        "fmt": "scientific",
        "precision": 6,
        "tol_abs": 1e-12,
        "tol_rel": 1e-9,
        "round_half": "even",
        "array_reorder": False,
    }
    prov = build_provenance(
        generated_by="ac 0.1.0-dev",
        sources=[],
        numeric_policy=custom_snapshot,
    )

    snapshot = prov["numeric_policy"]
    assert snapshot["fmt"] == "scientific"
    assert snapshot["precision"] == 6
    assert snapshot["tol_abs"] == pytest.approx(1e-12)
    assert snapshot["tol_rel"] == pytest.approx(1e-9)


def test_build_provenance_without_policy_is_null_numeric_policy() -> None:
    prov = build_provenance(
        generated_by="ac 0.1.0-dev", sources=None, numeric_policy=None
    )
    assert prov["numeric_policy"] is None
