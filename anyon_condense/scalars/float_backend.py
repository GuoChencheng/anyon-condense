from __future__ import annotations

import math
from typing import Iterable, Sequence

from anyon_condense.core.exceptions import NumericFieldError

__all__ = [
    "is_finite",
    "is_negative_zero",
    "normalize_float",
    "safe_sum",
    "linalg_norm_2",
]


# ---------- 基础判定 ----------


def is_finite(x: float) -> bool:
    """Return True if x is finite (neither NaN nor ±Inf)."""

    return math.isfinite(x)


def is_negative_zero(x: float) -> bool:
    """Detect IEEE-754 negative zero. Works for +0.0 and -0.0 only."""

    return x == 0.0 and math.copysign(1.0, x) < 0.0


def normalize_float(x: float) -> float:
    """
    Normalize a float into the project's canonical form:
      - Reject NaN/±Inf (raise NumericFieldError)
      - Convert -0.0 to +0.0
    """

    if not math.isfinite(x):
        raise NumericFieldError(f"Non-finite float: {x!r}")
    if is_negative_zero(x):
        return 0.0
    return x


# ---------- 安全求和（Neumaier） ----------


def safe_sum(xs: Iterable[float]) -> float:
    """
    Neumaier compensated summation.
    Precision close to math.fsum with O(n) time, O(1) extra space.

    Returns:
        A finite float with canonical zero (+0.0).
    Raises:
        NumericFieldError: if any term is non-finite.
    """

    s = 0.0
    c = 0.0
    for raw in xs:
        if not math.isfinite(raw):
            raise NumericFieldError(f"Non-finite term in sum: {raw!r}")
        x = 0.0 if is_negative_zero(raw) else raw

        t = s + x
        if abs(s) >= abs(x):
            c += (s - t) + x
        else:
            c += (x - t) + s
        s = t

    out = s + c
    return normalize_float(out)


# ---------- 稳定二范数（缩放） ----------


def linalg_norm_2(v: Sequence[float]) -> float:
    """
    Stable Euclidean norm using scaling to avoid overflow/underflow:
        m = max(|v_i|);  if m == 0 -> 0
        return m * sqrt( sum_i (v_i/m)^2 )

    Each element must be finite; -0.0 is canonicalized to +0.0.
    """

    if not v:
        return 0.0

    m = 0.0
    for raw in v:
        if not math.isfinite(raw):
            raise NumericFieldError(f"Non-finite vector entry: {raw!r}")
        ax = abs(raw)
        if ax > m:
            m = ax

    if m == 0.0:
        return 0.0

    s = 0.0
    c = 0.0
    inv_m = 1.0 / m
    for raw in v:
        x = raw * inv_m
        y = x * x
        t = s + y
        if abs(s) >= abs(y):
            c += (s - t) + y
        else:
            c += (y - t) + s
        s = t

    out = m * math.sqrt(s + c)
    return normalize_float(out)
