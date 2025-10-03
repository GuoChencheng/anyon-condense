#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from importlib import metadata

from . import __version__
from .scalars.numeric_policy import policy_from_env


def _toolchain_info() -> str:
    py = f"py{sys.version_info.major}.{sys.version_info.minor}"

    def _ver(pkg: str) -> str:
        try:
            version = metadata.version(pkg)
            return f"{pkg}{version}"
        except Exception:
            return pkg

    return "|".join([py, _ver("ruff"), _ver("mypy")])


def _handle_numeric_command(args: argparse.Namespace) -> int:
    overrides: dict[str, object] = {}
    if args.fmt:
        overrides["fmt"] = args.fmt
    if args.precision is not None:
        overrides["precision"] = args.precision
    if args.tol_abs is not None:
        overrides["tol_abs"] = args.tol_abs
    if args.tol_rel is not None:
        overrides["tol_rel"] = args.tol_rel
    if args.round_half:
        overrides["round_half"] = args.round_half
    if args.array_reorder is not None:
        overrides["array_reorder"] = args.array_reorder
    if args.clip_small is not None:
        overrides["clip_small"] = args.clip_small

    policy = policy_from_env(os.environ, overrides or None)

    if args.show_policy:
        print(json.dumps(policy.snapshot(), sort_keys=True, indent=2))
        return 0

    print("No numeric subcommand executed. Use '--show-policy' to inspect settings.")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ac", description="Anyon-Condense CLI")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument(
        "--info", action="store_true", help="Print environment info and exit"
    )

    subparsers = parser.add_subparsers(dest="command")

    num_parser = subparsers.add_parser(
        "num",
        help="Numeric policy helpers",
        description="Inspect and override numeric policy",
    )
    num_parser.add_argument(
        "--show-policy",
        action="store_true",
        help="Print numeric policy snapshot",
    )
    num_parser.add_argument(
        "--fmt", choices=["auto", "fixed", "scientific"], help="Override fmt"
    )
    num_parser.add_argument("--precision", type=int, help="Override precision")
    num_parser.add_argument("--tol-abs", type=float, help="Override absolute tolerance")
    num_parser.add_argument("--tol-rel", type=float, help="Override relative tolerance")
    num_parser.add_argument(
        "--round-half", choices=["even", "away"], help="Override rounding mode"
    )
    num_parser.add_argument(
        "--array-reorder",
        dest="array_reorder",
        action="store_true",
        help="Enable scalar array reordering",
    )
    num_parser.add_argument(
        "--no-array-reorder",
        dest="array_reorder",
        action="store_false",
        help="Disable scalar array reordering",
    )
    num_parser.add_argument(
        "--clip-small",
        dest="clip_small",
        action="store_true",
        help="Enable clipping of small values",
    )
    num_parser.add_argument(
        "--no-clip-small",
        dest="clip_small",
        action="store_false",
        help="Disable clipping of small values",
    )
    num_parser.set_defaults(array_reorder=None, clip_small=None)

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

    if args.command == "num":
        return _handle_numeric_command(args)

    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover - manual invocation guard
    raise SystemExit(main())
