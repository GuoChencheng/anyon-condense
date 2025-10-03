import subprocess
import sys


def test_cli_version_returns_zero_and_contains_version():
    proc = subprocess.run(
        [sys.executable, "-m", "anyon_condense.cli", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    out = (proc.stdout or "").strip()
    assert out, "version output is empty"


def test_cli_info_returns_zero_and_contains_keywords():
    proc = subprocess.run(
        [sys.executable, "-m", "anyon_condense.cli", "--info"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    out = proc.stdout.lower()
    assert "python=" in out
    assert "anyon-condense=" in out or "anyon_condense=" in out


def test_cli_no_args_prints_help_and_zero_exit():
    proc = subprocess.run(
        [sys.executable, "-m", "anyon_condense.cli"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "usage:" in (proc.stdout or "").lower()
