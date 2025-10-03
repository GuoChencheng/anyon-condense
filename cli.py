#!/usr/bin/env python3

import argparse
import platform

from anyon_condense import __version__


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ac", description="Anyon Condense CLI (skeleton)"
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument(
        "--info", action="store_true", help="Print environment info and exit"
    )
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    if args.info:
        python_version = platform.python_version()
        system_name = platform.system()
        machine_arch = platform.machine()
        print(f"python={python_version}  system={system_name}-{machine_arch}")
        print(f"anyon-condense={__version__}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
