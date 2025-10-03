from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal, localcontext
from typing import Any, List, Mapping, Optional, Sequence, Union

from anyon_condense.core.exceptions import NumericFieldError
from anyon_condense.scalars.float_backend import is_finite, normalize_float

Number = Union[int, float]

ROUNDING_MAP = {
    "even": ROUND_HALF_EVEN,
    "away": ROUND_HALF_UP,
}

__all__ = [
    "NumericPolicy",
    "clip_small",
    "approx_equal",
    "format_float",
    "reorder_scalar_array",
    "policy_from_env",
]


@dataclass(frozen=True)
class NumericPolicy:
    """Central numeric configuration for float comparisons and formatting."""

    mode: str = "float"
    tol_abs: float = 1e-10
    tol_rel: float = 1e-10
    fmt: str = "auto"
    precision: int = 12
    round_half: str = "even"
    array_reorder: bool = False
    clip_small: bool = True

    def __post_init__(self) -> None:
        if self.mode != "float":
            raise ValueError("Only mode='float' is supported in M2.")
        if self.fmt not in {"auto", "fixed", "scientific"}:
            raise ValueError("fmt must be 'auto' | 'fixed' | 'scientific'.")
        if self.round_half not in ROUNDING_MAP:
            raise ValueError("round_half must be 'even' | 'away'.")
        if self.precision <= 0:
            raise ValueError("precision must be positive.")
        if not (math.isfinite(self.tol_abs) and self.tol_abs >= 0.0):
            raise ValueError("tol_abs must be finite and >= 0.")
        if not (math.isfinite(self.tol_rel) and self.tol_rel >= 0.0):
            raise ValueError("tol_rel must be finite and >= 0.")

    def snapshot(self) -> dict:
        """Return a JSON-safe copy of the policy for provenance snapshots."""

        return {
            "mode": self.mode,
            "tol_abs": self.tol_abs,
            "tol_rel": self.tol_rel,
            "fmt": self.fmt,
            "precision": self.precision,
            "round_half": self.round_half,
            "array_reorder": self.array_reorder,
            "clip_small": self.clip_small,
        }


def _clip_small_value(x: float, policy: NumericPolicy) -> float:
    if not policy.clip_small:
        return x
    threshold = 10.0 ** (-(policy.precision + 1))
    if abs(x) < threshold:
        return 0.0
    return x


def clip_small(x: float, policy: NumericPolicy) -> float:
    if not is_finite(x):
        raise NumericFieldError(f"Non-finite float: {x!r}")
    x = normalize_float(x)
    x = _clip_small_value(x, policy)
    return normalize_float(x)


def approx_equal(a: float, b: float, policy: NumericPolicy) -> bool:
    a = clip_small(a, policy)
    b = clip_small(b, policy)
    diff = abs(a - b)
    eps = max(policy.tol_abs, policy.tol_rel * max(abs(a), abs(b)))
    return diff <= eps


def _decimal_from_float(x: float) -> Decimal:
    return Decimal.from_float(x)


def _format_scientific(x: float, precision: int, rounding_key: str) -> str:
    if x == 0.0:
        return "0e+0"

    sign = "-" if x < 0 else ""
    ax = abs(x)
    with localcontext() as ctx:
        ctx.prec = precision + 5
        ctx.rounding = ROUNDING_MAP[rounding_key]
        d = _decimal_from_float(ax)
        exponent = d.adjusted()
        scaled = d.scaleb(-exponent)
        quant = Decimal(1).scaleb(-(precision - 1))
        mantissa = scaled.quantize(quant, rounding=ROUNDING_MAP[rounding_key])
        if mantissa == Decimal("0"):
            exponent = 0
        elif mantissa >= Decimal("10"):
            mantissa = mantissa / Decimal(10)
            exponent += 1
        mantissa = mantissa.normalize()

    mantissa_exp = int(mantissa.as_tuple().exponent)
    if mantissa_exp >= 0:
        mantissa_str = format(mantissa, "f")
    else:
        mantissa_str = str(mantissa)
    if mantissa_str.endswith(".0"):
        mantissa_str = mantissa_str[:-2]
    exp_part = f"e{exponent:+d}"
    return f"{sign}{mantissa_str}{exp_part}"


def _format_fixed(x: float, precision: int, rounding_key: str) -> str:
    with localcontext() as ctx:
        ctx.rounding = ROUNDING_MAP[rounding_key]
        d = _decimal_from_float(x)
        quant = Decimal(1).scaleb(-precision)
        y = d.quantize(quant, rounding=ROUNDING_MAP[rounding_key])
    if y == Decimal("0"):
        y = Decimal("0")
    return f"{y:.{precision}f}"


def _auto_fixed(x: float, dp: int, rounding_key: str) -> str:
    with localcontext() as ctx:
        ctx.rounding = ROUNDING_MAP[rounding_key]
        d = _decimal_from_float(x)
        quant = Decimal(1).scaleb(-dp)
        y = d.quantize(quant, rounding=ROUNDING_MAP[rounding_key])
    if y == Decimal("0"):
        y = Decimal("0")
    return f"{y:.{dp}f}"


def format_float(x: float, policy: NumericPolicy) -> str:
    x = clip_small(x, policy)

    if policy.fmt == "scientific":
        return _format_scientific(x, policy.precision, policy.round_half)

    if policy.fmt == "fixed":
        return _format_fixed(x, policy.precision, policy.round_half)

    # auto mode
    if x == 0.0:
        return "0"
    ax = abs(x)
    if 1e-4 <= ax < 1e6:
        k = math.floor(math.log10(ax))
        dp = max(0, policy.precision - 1 - k)
        return _auto_fixed(x, dp, policy.round_half)
    return _format_scientific(x, policy.precision, policy.round_half)


def reorder_scalar_array(arr: Sequence[Number], policy: NumericPolicy) -> List[Number]:
    processed: List[Number] = []
    for item in arr:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            result: List[Number] = []
            for original in arr:
                if isinstance(original, float):
                    result.append(clip_small(original, policy))
                else:
                    result.append(original)
            return result
        processed.append(clip_small(float(item), policy))

    if not policy.array_reorder:
        return processed

    processed.sort()
    return processed


def policy_from_env(
    env: Optional[Mapping[str, str]] = None,
    overrides: Optional[Mapping[str, object]] = None,
) -> NumericPolicy:
    env = env or {}
    kwargs: dict[str, Any] = {}

    fmt = env.get("AC_NUMERIC_FMT")
    if fmt:
        kwargs["fmt"] = fmt

    prec = env.get("AC_NUMERIC_PREC")
    if prec:
        kwargs["precision"] = int(prec)

    tol_abs = env.get("AC_TOL_ABS")
    if tol_abs:
        kwargs["tol_abs"] = float(tol_abs)

    tol_rel = env.get("AC_TOL_REL")
    if tol_rel:
        kwargs["tol_rel"] = float(tol_rel)

    array_reorder = env.get("AC_ARRAY_REORDER")
    if array_reorder is not None:
        kwargs["array_reorder"] = array_reorder.lower() in {"1", "true", "yes", "on"}

    round_half = env.get("AC_ROUND_HALF")
    if round_half:
        kwargs["round_half"] = round_half

    clip_small_env = env.get("AC_CLIP_SMALL")
    if clip_small_env is not None:
        kwargs["clip_small"] = clip_small_env.lower() in {"1", "true", "yes", "on"}

    if overrides:
        kwargs.update(overrides)

    return NumericPolicy(**kwargs)
