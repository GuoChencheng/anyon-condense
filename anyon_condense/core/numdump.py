from __future__ import annotations

import math
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal, localcontext
from typing import Any, Sequence, Union

from anyon_condense.core.exceptions import NumericFieldError
from anyon_condense.core.utils import canonical_json_dump
from anyon_condense.scalars.float_backend import normalize_float
from anyon_condense.scalars.numeric_policy import NumericPolicy, clip_small

Number = Union[int, float]

ROUNDING_MAP = {
    "even": ROUND_HALF_EVEN,
    "away": ROUND_HALF_UP,
}

MIDRANGE_LOW = 1e-4
MIDRANGE_HIGH = 1e6


def _quantize_float(x: float, policy: NumericPolicy) -> float:
    """Apply clipping and rounding defined by the numeric policy to a float."""

    x = normalize_float(x)
    x = clip_small(x, policy)
    if x == 0.0:
        return 0.0

    rounding = ROUNDING_MAP[policy.round_half]
    abs_x = abs(x)
    with localcontext() as ctx:
        ctx.prec = policy.precision + 6
        ctx.rounding = rounding
        d = Decimal.from_float(x)

        if policy.fmt == "fixed":
            quant = Decimal(1).scaleb(-policy.precision)
            y = d.quantize(quant, rounding=rounding)

        elif policy.fmt == "scientific":
            sign = -1 if x < 0 else 1
            exponent = int(math.floor(math.log10(abs_x)))
            dec_abs = Decimal.from_float(abs_x)
            scaled = dec_abs / (Decimal(10) ** exponent)
            quant = Decimal(1).scaleb(-(policy.precision - 1))
            mantissa = scaled.quantize(quant, rounding=rounding)
            if mantissa >= Decimal(10):
                mantissa /= Decimal(10)
                exponent += 1
            y = mantissa * (Decimal(10) ** exponent)
            if sign < 0:
                y = -y

        else:  # auto
            if MIDRANGE_LOW <= abs_x < MIDRANGE_HIGH:
                exponent = math.floor(math.log10(abs_x))
                dp = max(0, policy.precision - 1 - exponent)
                quant = Decimal(1).scaleb(-dp)
                y = d.quantize(quant, rounding=rounding)
            else:
                sign = -1 if x < 0 else 1
                dec_abs = Decimal.from_float(abs_x)
                exponent = int(math.floor(math.log10(abs_x)))
                scaled = dec_abs / (Decimal(10) ** exponent)
                quant = Decimal(1).scaleb(-(policy.precision - 1))
                mantissa = scaled.quantize(quant, rounding=rounding)
                if mantissa >= Decimal(10):
                    mantissa /= Decimal(10)
                    exponent += 1
                y = mantissa * (Decimal(10) ** exponent)
                if sign < 0:
                    y = -y

    xf = float(y)
    if not math.isfinite(xf):
        raise NumericFieldError(f"Quantization overflow: {y!r}")
    return normalize_float(xf)


def _is_flat_numeric_array(seq: Sequence[Any]) -> bool:
    if not isinstance(seq, (list, tuple)):
        return False
    for value in seq:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
    return True


def _normalize_any(
    obj: Any, policy: NumericPolicy, *, inside_array: bool = False
) -> Any:
    if isinstance(obj, float):
        return _quantize_float(obj, policy)

    if isinstance(obj, (int, str, bool)) or obj is None:
        return obj

    if isinstance(obj, dict):
        result: dict[Any, Any] = {}
        for key, value in obj.items():
            result[key] = _normalize_any(value, policy, inside_array=False)
        return result

    if isinstance(obj, (list, tuple)):
        normalized = [_normalize_any(value, policy, inside_array=True) for value in obj]
        if (
            policy.array_reorder
            and not inside_array
            and _is_flat_numeric_array(normalized)
        ):
            normalized.sort()
        return normalized if isinstance(obj, list) else tuple(normalized)

    return obj


def normalize_payload_numbers(payload: Any, policy: NumericPolicy) -> Any:
    """Deep-copy-like numeric normalization respecting the given policy."""

    return _normalize_any(payload, policy, inside_array=False)


def normalized_canonical_dump(payload: Any, policy: NumericPolicy) -> str:
    """Normalize numeric values then emit the canonical JSON string."""

    normalized = normalize_payload_numbers(payload, policy)
    return canonical_json_dump(normalized)
