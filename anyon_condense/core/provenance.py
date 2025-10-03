"""Provenance helpers ensure minimal tracing metadata on outputs."""

from __future__ import annotations

import sys
from datetime import datetime as _datetime
from datetime import timezone as _timezone
from typing import Any, Dict, Optional, Sequence

from anyon_condense import __version__ as _AC_VERSION

try:  # Python 3.8+: importlib.metadata
    from importlib import metadata as _im
except Exception:  # pragma: no cover - fallback for very old Python
    _im = None  # type: ignore[assignment]


def _iso_utc_now() -> str:
    """Return current UTC time formatted as ISO8601 with trailing 'Z'."""

    return (
        _datetime.now(_timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _pkg_version_token(pkg: str) -> str:
    if _im is None:
        return pkg
    try:
        return f"{pkg}{_im.version(pkg)}"
    except Exception:  # pragma: no cover - pkg info may be missing
        return pkg


def _toolchain_version() -> str:
    py = f"py{sys.version_info.major}.{sys.version_info.minor}"
    return "|".join([py, _pkg_version_token("ruff"), _pkg_version_token("mypy")])


def build_provenance(
    sources: Optional[Sequence[str]] = None,
    *,
    generated_by: Optional[str] = None,
    exact_backend_id: Optional[str] = None,
    numeric_policy: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    src_list = [str(s) for s in sources] if sources else ["<unspecified>"]
    if not src_list:
        src_list = ["<unspecified>"]
    return {
        "generated_by": generated_by or f"ac {_AC_VERSION}",
        "date": _iso_utc_now(),
        "toolchain_version": _toolchain_version(),
        "exact_backend_id": exact_backend_id,
        "numeric_policy": numeric_policy,
        "sources": src_list,
    }


def ensure_provenance_inplace(payload: Dict[str, Any]) -> None:
    """Ensure payload contains minimal provenance (merge-only, never overwrite)."""

    tmp_sources = None
    if isinstance(payload.get("_sources"), list):
        tmp_sources = [
            str(s) for s in payload.get("_sources", []) if isinstance(s, str)
        ]
    payload.pop("_sources", None)

    base = build_provenance(tmp_sources)
    if not isinstance(payload.get("provenance"), dict):
        payload["provenance"] = base
        return

    prov = payload["provenance"]
    for key, value in base.items():
        prov.setdefault(key, value)
