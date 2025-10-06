from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable
SCRIPT = Path("tools") / "demo_m2_numdump.py"


def run_demo(
    *argv: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    command = [PYTHON, str(SCRIPT), *argv]
    return subprocess.run(command, capture_output=True, text=True, env=env)


def test_demo_script_basic(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(
        json.dumps({"x": 0.000000000001, "y": 1.23456789}), encoding="utf-8"
    )

    result = run_demo("--in", str(payload_path))
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert any(line.startswith("POLICY:") for line in lines)
    assert any(line.startswith("BEFORE:") for line in lines)
    assert any(line.startswith("AFTER :") for line in lines)
    assert any(line.startswith("SHA256(normalized):") for line in lines)


def test_demo_script_overrides(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps({"x": 1.23456}), encoding="utf-8")

    result = run_demo("--in", str(payload_path), "--fmt", "fixed", "--precision", "3")
    assert result.returncode == 0
    assert "AFTER :" in result.stdout


def test_demo_script_reject_nan(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps({"x": float("nan")}), encoding="utf-8")

    result = run_demo("--in", str(payload_path))
    assert result.returncode == 2
    assert "Numeric error" in result.stderr
