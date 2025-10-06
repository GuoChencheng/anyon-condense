from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

import pytest

from anyon_condense.core.consistency.modular import check_modular_relations
from anyon_condense.core.hashing import sha256_of_payload_normalized
from anyon_condense.core.numdump import normalized_canonical_dump
from anyon_condense.core.provenance import build_provenance
from anyon_condense.scalars.numeric_policy import NumericPolicy

PYTHON = sys.executable


def run_cli(
    *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    command = [PYTHON, "-m", "anyon_condense.cli", "num", *args]
    return subprocess.run(
        command, capture_output=True, text=True, env=env or os.environ.copy()
    )


def toric_st() -> tuple[List[List[float]], List[List[float]]]:
    s = [
        [0.5, 0.5, 0.5, 0.5],
        [0.5, 0.5, -0.5, -0.5],
        [0.5, -0.5, 0.5, -0.5],
        [0.5, -0.5, -0.5, 0.5],
    ]
    t = [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, -1.0],
    ]
    return s, t


def inject_noise(
    matrix: Iterable[Iterable[float]], epsilon: float
) -> List[List[float]]:
    result: List[List[float]] = []
    sign = 1.0
    for row in matrix:
        new_row: List[float] = []
        for value in row:
            new_row.append(value + sign * epsilon)
            sign = -sign
        result.append(new_row)
    return result


def test_cli_show_policy_contains_required_keys() -> None:
    result = run_cli("show-policy")
    assert result.returncode == 0, result.stderr
    output = result.stdout.strip()
    for key in ("tol_abs", "tol_rel", "precision", "fmt"):
        assert key in output, f"missing {key} in show-policy output: {output}"


def test_cli_dump_outputs_prefix_and_sha256(tmp_path: Path) -> None:
    payload_path = tmp_path / "input.json"
    payload_path.write_text(json.dumps({"x": 1e-12, "y": 1.23456789}), encoding="utf-8")

    result = run_cli("dump", "--in", str(payload_path))
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert any(line.startswith("PREFIX: ") for line in lines), result.stdout
    sha_lines = [line for line in lines if line.startswith("SHA256: ")]
    assert sha_lines, result.stdout
    assert re.fullmatch(r"SHA256:\s*sha256:[0-9a-fA-F]{64}", sha_lines[-1])


def test_normalized_dump_and_hash_stability() -> None:
    payload_a = {"v": [0.000000000001, 1.23456789, -0.0]}
    payload_b = {"v": [1e-12, 1.23456789, -0.0]}
    policy = NumericPolicy(fmt="auto", precision=12)

    dump_a = normalized_canonical_dump(payload_a, policy)
    dump_b = normalized_canonical_dump(payload_b, policy)
    assert dump_a == dump_b

    hash_a = sha256_of_payload_normalized(payload_a, policy)
    hash_b = sha256_of_payload_normalized(payload_b, policy)
    assert hash_a == hash_b


def test_modular_check_tolerance_behavior() -> None:
    s, t = toric_st()
    default_policy = NumericPolicy(tol_abs=1e-10, tol_rel=1e-10)

    small_noise = check_modular_relations(inject_noise(s, 1e-12), t, default_policy)
    assert small_noise["status"] is True
    snapshot = small_noise["policy_snapshot"]
    assert snapshot["tol_abs"] == pytest.approx(1e-10)
    assert snapshot["tol_rel"] == pytest.approx(1e-10)

    big_noise = check_modular_relations(inject_noise(s, 1e-6), t, default_policy)
    assert big_noise["status"] is False

    loose_policy = NumericPolicy(tol_abs=1e-5, tol_rel=1e-5)
    loose_noise = check_modular_relations(inject_noise(s, 1e-6), t, loose_policy)
    assert loose_noise["status"] is True
    assert loose_noise["policy_snapshot"]["tol_abs"] == pytest.approx(1e-5)


def test_provenance_includes_numeric_policy_snapshot() -> None:
    policy = NumericPolicy(fmt="auto", precision=12, tol_abs=1e-10, tol_rel=1e-10)
    provenance = build_provenance(
        generated_by="ac 0.1.0-dev",
        sources=["tests/examples/Vec_Z2_mfusion.json"],
        numeric_policy=policy,
    )
    snapshot = provenance["numeric_policy"]
    for key in (
        "fmt",
        "precision",
        "tol_abs",
        "tol_rel",
        "round_half",
        "array_reorder",
    ):
        assert key in snapshot
    assert snapshot["precision"] == 12
    assert snapshot["fmt"] == "auto"
    assert snapshot["tol_abs"] == pytest.approx(1e-10)
    assert snapshot["tol_rel"] == pytest.approx(1e-10)
