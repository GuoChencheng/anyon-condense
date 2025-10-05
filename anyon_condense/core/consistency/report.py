from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from anyon_condense.scalars.numeric_policy import NumericPolicy


def _policy_minimal_snapshot(policy: NumericPolicy) -> Dict[str, Any]:
    """Build a reproducible snapshot for provenance/reporting."""

    snap = policy.snapshot()
    subset = {
        "fmt": snap["fmt"],
        "precision": snap["precision"],
        "tol_abs": snap["tol_abs"],
        "tol_rel": snap["tol_rel"],
    }
    subset["round_half"] = snap.get("round_half")
    subset["array_reorder"] = snap.get("array_reorder")
    subset["clip_small"] = snap.get("clip_small")
    subset["mode"] = snap.get("mode", "float")
    return subset


@dataclass
class Report:
    """Structured result used by consistency checks."""

    status: bool
    metrics: Dict[str, float] = field(default_factory=dict)
    policy_snapshot: Dict[str, Any] = field(default_factory=dict)
    notes: Optional[str] = None

    @classmethod
    def from_policy(
        cls,
        status: bool,
        metrics: Mapping[str, float] | None,
        policy: NumericPolicy,
        notes: Optional[str] = None,
    ) -> "Report":
        return cls(
            status=status,
            metrics={name: float(value) for name, value in (metrics or {}).items()},
            policy_snapshot=_policy_minimal_snapshot(policy),
            notes=notes,
        )

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "status": bool(self.status),
            "metrics": dict(self.metrics),
            "policy_snapshot": dict(self.policy_snapshot),
        }
        if self.notes is not None:
            payload["notes"] = self.notes
        return payload

    def set_metric(self, name: str, value: float) -> None:
        self.metrics[name] = float(value)

    def merge_metrics(self, extra: Mapping[str, float]) -> None:
        for key, value in extra.items():
            self.set_metric(key, value)


__all__ = ["Report"]
