#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import sys as _sys
from typing import List, Optional, Tuple

# Ensure repository root is importable when running this script directly
_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_ROOT))

EXAMPLE_DEFAULT = pathlib.Path("tests/examples/Vec_Z2_mfusion.json")


def _get_ac_modules() -> Tuple:
    """Import anyon_condense helpers lazily to satisfy linting rules."""

    from anyon_condense.core.hashing import (
        sha256_of_payload as _sha256_of_payload,
    )  # noqa: WPS433
    from anyon_condense.core.io import (
        load_mfusion_input as _load_mfusion_input,
    )  # noqa: WPS433
    from anyon_condense.core.utils import (
        canonical_json_dump as _canonical_json_dump,
    )  # noqa: WPS433

    return _sha256_of_payload, _load_mfusion_input, _canonical_json_dump


def _resolve_path(path: pathlib.Path) -> pathlib.Path:
    if path.is_absolute():
        return path
    root = pathlib.Path(__file__).resolve().parents[1]
    return root / path


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="M1 Demo: load+validate mfusion, print canonical & sha256"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=str(EXAMPLE_DEFAULT),
        help=f"Path to mfusion input JSON (default: {EXAMPLE_DEFAULT})",
    )
    args = parser.parse_args(argv)

    target = _resolve_path(pathlib.Path(args.path))
    print(f"[demo] Using example: {target}")

    sha256_of_payload, load_mfusion_input, canonical_json_dump = _get_ac_modules()

    payload = load_mfusion_input(target)
    objects = payload.get("simple_objects", [])
    print(f"[demo] Loaded mfusion input OK. objects={objects}")

    canonical = canonical_json_dump(payload)
    preview = canonical[:120] + ("..." if len(canonical) > 120 else "")
    print("[demo] canonical (first 120 chars):")
    print(preview)

    digest = sha256_of_payload(payload)
    print(f"[demo] sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
