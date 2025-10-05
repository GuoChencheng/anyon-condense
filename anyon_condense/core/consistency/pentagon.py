from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple, Union

from anyon_condense.core.consistency.numcheck import approx_equal_number
from anyon_condense.scalars.numeric_policy import NumericPolicy

Number = Union[int, float, complex]


def check_pentagon_equations(
    equations: Iterable[Tuple[Number, Number]], policy: NumericPolicy
) -> Dict[str, Any]:
    total = 0
    failed = 0
    for lhs, rhs in equations:
        total += 1
        if not approx_equal_number(lhs, rhs, policy):
            failed += 1
    return {"status": failed == 0, "failed": failed, "total": total}
