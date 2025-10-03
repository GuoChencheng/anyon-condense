"""Module entry point wired to the CLI skeleton."""

from .cli import main

if __name__ == "__main__":  # pragma: no cover - exercised via subprocess
    raise SystemExit(main())
