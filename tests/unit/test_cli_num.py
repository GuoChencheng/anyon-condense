from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable
MODULE = "anyon_condense.cli"


def run_cli(
    *argv: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    command = [PYTHON, "-m", MODULE, *argv]
    return subprocess.run(command, capture_output=True, text=True, env=env)


def _clean_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in ["AC_NUMERIC_FMT", "AC_NUMERIC_PREC", "AC_TOL_ABS", "AC_TOL_REL"]:
        env.pop(key, None)
    return env


def test_num_show_policy_default_env() -> None:
    env = _clean_env()
    result = run_cli("num", "--show-policy", env=env)
    assert result.returncode == 0
    assert '"fmt":"auto"' in result.stdout
    assert '"precision":12' in result.stdout


def test_num_show_policy_env_overrides() -> None:
    env = os.environ.copy()
    env["AC_NUMERIC_FMT"] = "scientific"
    env["AC_NUMERIC_PREC"] = "6"
    result = run_cli("num", "--show-policy", env=env)
    assert result.returncode == 0
    assert '"fmt":"scientific"' in result.stdout
    assert '"precision":6' in result.stdout


def test_num_dump_basic(tmp_path: Path) -> None:
    payload_path = tmp_path / "in.json"
    payload_path.write_text(
        json.dumps({"x": 1.0e-12, "y": 1.23456789}), encoding="utf-8"
    )

    result = run_cli("num", "--dump", "--in", str(payload_path))
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert lines[0].startswith("PREFIX: {")
    assert lines[1].startswith("SHA256: sha256:")


def test_num_dump_with_cli_overrides(tmp_path: Path) -> None:
    payload_path = tmp_path / "in.json"
    payload_path.write_text(json.dumps({"x": 1.23456}), encoding="utf-8")

    result = run_cli(
        "num",
        "--dump",
        "--in",
        str(payload_path),
        "--fmt",
        "fixed",
        "--precision",
        "3",
    )
    assert result.returncode == 0
    assert "1.235" in result.stdout


def test_num_dump_file_not_found() -> None:
    result = run_cli("num", "--dump", "--in", "no_such.json")
    assert result.returncode == 2
    assert "File not found" in result.stderr
