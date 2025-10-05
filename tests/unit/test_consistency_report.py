from __future__ import annotations

import pytest

from anyon_condense.core.consistency.report import Report
from anyon_condense.scalars.numeric_policy import NumericPolicy


def test_report_has_policy_snapshot_and_metrics():
    policy = NumericPolicy(fmt="scientific", precision=6, tol_abs=1e-12, tol_rel=1e-9)
    report = Report.from_policy(
        status=True,
        metrics={"max_err": 3.14e-12, "violations": 0.0},
        policy=policy,
        notes="smoke",
    )

    payload = report.to_dict()
    assert payload["status"] is True
    assert payload["metrics"]["max_err"] == pytest.approx(3.14e-12)
    snapshot = payload["policy_snapshot"]
    assert snapshot["fmt"] == "scientific"
    assert snapshot["precision"] == 6
    assert snapshot["tol_abs"] == pytest.approx(1e-12)
    assert snapshot["tol_rel"] == pytest.approx(1e-9)
    assert "round_half" in snapshot
    assert "array_reorder" in snapshot
    assert "clip_small" in snapshot
    assert snapshot.get("mode") == "float"
    assert payload["notes"] == "smoke"


def test_report_mutation_helpers():
    policy = NumericPolicy()
    report = Report.from_policy(True, metrics=None, policy=policy)
    report.set_metric("a", 1.0)
    report.merge_metrics({"b": 2.5})
    payload = report.to_dict()
    assert payload["metrics"]["a"] == pytest.approx(1.0)
    assert payload["metrics"]["b"] == pytest.approx(2.5)
