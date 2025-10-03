"""
Module entry point: `python -m anyon_condense`
"""

from . import __version__


def main() -> None:
    print(f"anyon-condense {__version__}")


if __name__ == "__main__":
    main()
