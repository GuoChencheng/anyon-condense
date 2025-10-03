import logging
import subprocess
import sys

from anyon_condense.core.logging import get_logger


def test_caplog_captures_one_info(caplog):
    caplog.set_level(logging.INFO)
    log = get_logger("test.h3.logging", level="INFO")
    log.info("h3-info-smoke")
    assert any(
        rec.levelname == "INFO"
        and rec.name == "test.h3.logging"
        and "h3-info-smoke" in rec.message
        for rec in caplog.records
    )


def test_cli_version_zero_and_contains_version():
    proc = subprocess.run(
        [sys.executable, "-m", "anyon_condense.cli", "--version"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    out = (proc.stdout or "").strip()
    assert out, "version output is empty"


def test_cli_info_zero_and_contains_keywords():
    proc = subprocess.run(
        [sys.executable, "-m", "anyon_condense.cli", "--info"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    lo = (proc.stdout or "").lower()
    assert "python=" in lo
    assert "anyon-condense=" in lo or "anyon_condense=" in lo
