"""Командний рядок: kzp-lab07 <input.csv> <report.txt> [--ratings]."""

import argparse
import sys
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from kzp_lab07.analysis import HIGH_AVERAGE_THRESHOLD, make_summary
from kzp_lab07.errors import DataError
from kzp_lab07.loader import load_learners
from kzp_lab07.reporting import format_report, write_report

EXIT_OK = 0
EXIT_DATA_ERROR = 1
EXIT_IO_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """Створює розбирач аргументів."""
    parser = argparse.ArgumentParser(prog="kzp-lab07", description="Звіт за реєстром студентів.")
    parser.add_argument("--version", action="version", version=f"kzp-lab07 {_package_version()}")
    parser.add_argument("input", type=Path, help="вхідний CSV")
    parser.add_argument("output", type=Path, help="файл звіту")
    parser.add_argument(
        "--threshold",
        type=float,
        default=HIGH_AVERAGE_THRESHOLD,
        help="поріг відбору за середнім балом (типово 90)",
    )
    parser.add_argument("--ratings", action="store_true", help="додати рейтинг груп")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Запускає програму й повертає код завершення (0 - успіх)."""
    args = build_parser().parse_args(argv)
    _use_utf8_streams()
    try:
        learners = load_learners(args.input)
        text = format_report(make_summary(learners, args.threshold), args.ratings)
        write_report(args.output, text)
    except DataError as error:
        print(f"Помилка даних: {error}", file=sys.stderr)
        return EXIT_DATA_ERROR
    except OSError as error:
        print(f"Помилка запису звіту: {error}", file=sys.stderr)
        return EXIT_IO_ERROR
    print(text, end="")
    return EXIT_OK


def _package_version() -> str:
    """Повертає версію встановленого пакета або "unknown", якщо пакет не встановлено."""
    try:
        return version("kzp-lab67")
    except PackageNotFoundError:
        return "unknown"


def _use_utf8_streams() -> None:
    """Задає UTF-8 і роздільник рядків \\n для stdout і stderr, щоб вивід не залежав від ОС."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", newline="\n")


if __name__ == "__main__":
    sys.exit(main())
