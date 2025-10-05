#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from importlib import metadata

from anyon_condense.core.exceptions import (
    CanonicalizationError,
    HashingError,
    NumericFieldError,
)
from anyon_condense.core.hashing import sha256_of_payload
from anyon_condense.core.numdump import normalize_payload_numbers
from anyon_condense.core.utils import canonical_json_dump
from anyon_condense.scalars.numeric_policy import NumericPolicy
from anyon_condense.utils.profiles import get_numeric_policy

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


def _build_numeric_policy(args: argparse.Namespace) -> NumericPolicy:
    overrides: dict[str, object] = {}
    if args.fmt:
        overrides["fmt"] = args.fmt
    if args.precision is not None:
        overrides["precision"] = args.precision
    if args.tol_abs is not None:
        overrides["tol_abs"] = args.tol_abs
    if args.tol_rel is not None:
        overrides["tol_rel"] = args.tol_rel
    if getattr(args, "round_half", None):
        overrides["round_half"] = args.round_half
    if getattr(args, "array_reorder", None) is not None:
        overrides["array_reorder"] = args.array_reorder
    if getattr(args, "clip_small", None) is not None:
        overrides["clip_small"] = args.clip_small

    return get_numeric_policy(env=os.environ, overrides=overrides or None)


def _handle_num_show_policy(policy) -> int:
    print(canonical_json_dump(policy.snapshot()))
    return 0


def _handle_num_dump(args: argparse.Namespace, policy) -> int:
    if not args.dump:
        return 1

    if not args.input:
        print(
            "[ac:num] Missing required '--in' path when using --dump.", file=sys.stderr
        )
        return 2

    try:
        with open(args.input, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError:
        print(f"[ac:num] File not found: {args.input}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(
            f"[ac:num] JSON decode error in {args.input}: {exc}",
            file=sys.stderr,
        )
        return 2

    try:
        normalized = normalize_payload_numbers(payload, policy)
    except NumericFieldError as exc:
        print(f"[ac:num] Numeric error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - unexpected failures
        print(f"[ac:num] Unexpected error during normalization: {exc}", file=sys.stderr)
        return 2

    try:
        canonical = canonical_json_dump(normalized)
    except CanonicalizationError as exc:
        print(f"[ac:num] Canonicalization error: {exc}", file=sys.stderr)
        return 2

    try:
        digest = sha256_of_payload(normalized)
    except HashingError as exc:
        print(f"[ac:num] Hashing error: {exc}", file=sys.stderr)
        return 2

    print(f"PREFIX: {canonical[:120]}")
    print(f"SHA256: {digest}")
    return 0


def _handle_numeric_command(
    args: argparse.Namespace, num_parser: argparse.ArgumentParser
) -> int:
    policy = _build_numeric_policy(args)

    if args.show_policy:
        return _handle_num_show_policy(policy)

    if args.dump:
        return _handle_num_dump(args, policy)

    num_parser.print_help()
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ac", description="Anyon-Condense CLI")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument(
        "--info", action="store_true", help="Print environment info and exit"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Common numeric policy override flags (reused across forms)
    num_common = argparse.ArgumentParser(add_help=False)
    num_common.add_argument(
        "--fmt", choices=["auto", "fixed", "scientific"], help="Override fmt"
    )
    num_common.add_argument("--precision", type=int, help="Override precision")
    num_common.add_argument("--tol-abs", type=float, help="Override absolute tolerance")
    num_common.add_argument("--tol-rel", type=float, help="Override relative tolerance")
    num_common.add_argument(
        "--round-half", choices=["even", "away"], help="Override rounding mode"
    )
    num_common.add_argument(
        "--array-reorder",
        dest="array_reorder",
        action="store_true",
        help="Enable scalar array reordering",
    )
    num_common.add_argument(
        "--no-array-reorder",
        dest="array_reorder",
        action="store_false",
        help="Disable scalar array reordering",
    )
    num_common.add_argument(
        "--clip-small",
        dest="clip_small",
        action="store_true",
        help="Enable clipping of small values",
    )
    num_common.add_argument(
        "--no-clip-small",
        dest="clip_small",
        action="store_false",
        help="Disable clipping of small values",
    )

    num_parser = subparsers.add_parser(
        "num",
        help="Numeric policy helpers",
        description="Inspect and override numeric policy",
        parents=[num_common],
    )
    num_parser.set_defaults(array_reorder=None, clip_small=None)
    num_parser.add_argument(
        "--show-policy",
        action="store_true",
        help="Print numeric policy snapshot",
    )
    num_parser.add_argument(
        "--dump",
        action="store_true",
        help="Normalize and canonical-dump a JSON file",
    )
    num_parser.add_argument(
        "--in",
        dest="input",
        help="Path to input JSON for --dump",
    )

    # Subcommands for compatibility: `ac num show-policy` and `ac num dump ...`
    num_subparsers = num_parser.add_subparsers(dest="num_cmd")

    num_show = num_subparsers.add_parser(
        "show-policy",
        help="Show current NumericPolicy snapshot",
        parents=[num_common],
        add_help=True,
    )
    num_show.set_defaults(show_policy=True)

    num_dump = num_subparsers.add_parser(
        "dump",
        help="Normalize and canonical-dump a JSON file",
        parents=[num_common],
        add_help=True,
    )
    num_dump.add_argument(
        "--in", dest="input", required=True, help="Path to input JSON"
    )
    num_dump.set_defaults(dump=True)

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
        return _handle_numeric_command(args, num_parser)

    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover - manual invocation guard
    raise SystemExit(main())
