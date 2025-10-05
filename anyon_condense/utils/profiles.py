from __future__ import annotations

import os
from typing import Any, Dict, Mapping, Optional

from anyon_condense.scalars.numeric_policy import NumericPolicy

_TRUE_SET = {"1", "true", "yes", "on"}


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in _TRUE_SET


def get_numeric_policy(
    env: Mapping[str, str] = os.environ,
    overrides: Optional[Mapping[str, Any]] = None,
) -> NumericPolicy:
    """Construct a NumericPolicy using defaults overridden by env and explicit overrides."""

    kwargs: Dict[str, Any] = {}

    fmt = env.get("AC_NUMERIC_FMT")
    if fmt:
        kwargs["fmt"] = fmt

    precision = env.get("AC_NUMERIC_PREC")
    if precision:
        kwargs["precision"] = int(precision)

    tol_abs = env.get("AC_TOL_ABS")
    if tol_abs:
        kwargs["tol_abs"] = float(tol_abs)

    tol_rel = env.get("AC_TOL_REL")
    if tol_rel:
        kwargs["tol_rel"] = float(tol_rel)

    array_reorder = env.get("AC_ARRAY_REORDER")
    if array_reorder is not None:
        kwargs["array_reorder"] = _parse_bool(array_reorder)

    round_half = env.get("AC_ROUND_HALF")
    if round_half:
        kwargs["round_half"] = round_half

    clip_small = env.get("AC_CLIP_SMALL")
    if clip_small is not None:
        kwargs["clip_small"] = _parse_bool(clip_small)

    if overrides:
        kwargs.update(overrides)

    return NumericPolicy(**kwargs)
