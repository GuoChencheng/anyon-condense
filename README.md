[![CI](https://github.com/GuoChencheng/anyon-condense/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/GuoChencheng/anyon-condense/actions/workflows/ci.yml)

# anyon-condense (skeleton, M1-A1)

This is the minimal project skeleton for the Anyon-Condense pipeline.

## Quick start
```bash
pip install -e .
python -m anyon_condense
python cli.py --version
python - <<'PY'
from anyon_condense.core.io import load_mfusion_input, write_umtc_output

mfusion_doc = load_mfusion_input("tests/examples/Vec_Z2_mfusion.json")
write_umtc_output("tmp/umtc_output.json", mfusion_doc)
PY
```
