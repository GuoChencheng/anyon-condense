from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable


def run_cli(
    *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    cmd = [PYTHON, "-m", "anyon_condense.cli", "num", *args]
    return subprocess.run(
        cmd, capture_output=True, text=True, env=env or os.environ.copy()
    )


def test_show_policy_contains_required_keys_and_returncode_zero() -> None:
    result = run_cli("show-policy")
    assert result.returncode == 0, result.stderr
    output = result.stdout.strip()
    for key in ("tol_abs", "tol_rel", "precision", "fmt"):
        assert key in output, f"missing {key} in show-policy output: {output}"


def test_dump_returns_sha256_and_prefix_on_valid_json(tmp_path: Path) -> None:
    payload_path = tmp_path / "input.json"
    payload_path.write_text(json.dumps({"x": 1e-12, "y": 1.23456789}), encoding="utf-8")

    result = run_cli("dump", "--in", str(payload_path))
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert any(line.startswith("PREFIX: ") for line in lines), result.stdout
    sha_lines = [line for line in lines if line.startswith("SHA256: ")]
    assert sha_lines, result.stdout
    assert re.fullmatch(r"SHA256:\s*sha256:[0-9a-fA-F]{64}", sha_lines[-1])

    result_override = run_cli(
        "dump",
        "--in",
        str(payload_path),
        "--fmt",
        "fixed",
        "--precision",
        "6",
    )
    assert result_override.returncode == 0, result_override.stderr
    assert "PREFIX: " in result_override.stdout
    assert "SHA256: " in result_override.stdout


def test_env_overrides_show_policy_smoke() -> None:
    env = os.environ.copy()
    env["AC_NUMERIC_FMT"] = "scientific"
    env["AC_NUMERIC_PREC"] = "6"

    result = run_cli("show-policy", env=env)
    assert result.returncode == 0, result.stderr
    output = result.stdout.strip()
    assert '"fmt":"scientific"' in output or '"fmt": "scientific"' in output
    assert '"precision":6' in output or '"precision": 6' in output
