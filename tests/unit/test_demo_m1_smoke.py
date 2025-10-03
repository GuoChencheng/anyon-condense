import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO_SCRIPT = ROOT / "tools" / "demo_m1.py"


def test_demo_script_runs_and_prints_sha256():
    proc = subprocess.run(
        [sys.executable, str(DEMO_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert proc.returncode == 0
    stdout = proc.stdout
    assert "[demo] Using example" in stdout
    assert "Loaded mfusion input OK" in stdout
    assert "sha256:" in stdout
