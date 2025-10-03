"""Scalars utilities for numerical backends."""

from .float_backend import (
    is_finite,
    is_negative_zero,
    linalg_norm_2,
    normalize_float,
    safe_sum,
)
from .numeric_policy import (
    NumericPolicy,
    approx_equal,
    clip_small,
    format_float,
    policy_from_env,
    reorder_scalar_array,
)

__all__ = [
    "is_finite",
    "is_negative_zero",
    "normalize_float",
    "safe_sum",
    "linalg_norm_2",
    "NumericPolicy",
    "approx_equal",
    "clip_small",
    "format_float",
    "reorder_scalar_array",
    "policy_from_env",
]
