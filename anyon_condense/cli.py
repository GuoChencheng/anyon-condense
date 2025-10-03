#!/usr/bin/env python3
from __future__ import annotations

import argparse
import platform
import sys
from importlib import metadata

from . import __version__


def _toolchain_info() -> str:
    py = f"py{sys.version_info.major}.{sys.version_info.minor}"

    def _ver(pkg: str) -> str:
        try:
            version = metadata.version(pkg)
            return f"{pkg}{version}"
        except Exception:
            return pkg

    return "|".join([py, _ver("ruff"), _ver("mypy")])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ac",
        description="Anyon-Condense CLI (skeleton)",
        add_help=True,
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument(
        "--info", action="store_true", help="Print environment info and exit"
    )

    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    if args.info:
        print(
            f"python={platform.python_version()}  system={platform.system()}-{platform.machine()}"
        )
        print(f"anyon-condense={__version__}  toolchain={_toolchain_info()}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover - manual invocation guard
    raise SystemExit(main())
