"""Provenance helpers ensure minimal tracing metadata on outputs."""

from __future__ import annotations

import sys
from datetime import datetime as _datetime
from datetime import timezone as _timezone
from typing import Any, Dict, List, Optional, Sequence

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


def sanitize_sources(sources: Optional[Sequence[Any]]) -> List[str]:
    """Normalise incoming ``sources`` entries into trimmed strings."""

    if sources is None:
        return []

    items: Sequence[Any]
    if isinstance(sources, (str, bytes)):
        items = [sources]
    else:
        items = sources

    normalised: List[str] = []
    for entry in items:
        if entry is None:
            continue
        text = str(entry).strip()
        if not text:
            continue
        normalised.append(text)
    return normalised


def ensure_provenance_inplace(payload: Dict[str, Any]) -> None:
    """Ensure payload contains minimal provenance (merge-only, never overwrite)."""

    tmp_sources = sanitize_sources(payload.get("_sources"))
    payload.pop("_sources", None)

    base = build_provenance(tmp_sources or None)
    if not isinstance(payload.get("provenance"), dict):
        payload["provenance"] = base
        return

    prov = payload["provenance"]
    for key, value in base.items():
        prov.setdefault(key, value)


def append_sources_inplace(
    payload: Dict[str, Any], more_sources: Sequence[Any]
) -> None:
    """Merge additional ``more_sources`` into ``payload['provenance'].sources``."""

    ensure_provenance_inplace(payload)

    prov = payload.get("provenance")
    if not isinstance(prov, dict):  # Defensive, should not happen after ensure
        raise TypeError("payload['provenance'] must be a dict after ensure")

    base_norm = sanitize_sources(prov.get("sources"))
    add_norm = sanitize_sources(more_sources)

    seen = set(base_norm)
    merged: List[str] = list(base_norm)
    for source in add_norm:
        if source in seen:
            continue
        merged.append(source)
        seen.add(source)

    prov["sources"] = merged
