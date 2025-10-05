"""Consistency checks built on NumericPolicy-aware comparisons."""

from .hexagon import check_hexagon_equations
from .modular import check_modular_relations
from .numcheck import (
    approx_equal_matrices,
    approx_equal_number,
    approx_equal_vectors,
    max_abs_diff,
)
from .pentagon import check_pentagon_equations
from .report import Report

__all__ = [
    "approx_equal_matrices",
    "approx_equal_number",
    "approx_equal_vectors",
    "check_hexagon_equations",
    "check_modular_relations",
    "check_pentagon_equations",
    "max_abs_diff",
    "Report",
]
