"""Командний рядок: kzp-lab06 <input.csv> <report.txt>."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from kzp_lab06.analysis import HIGH_AVERAGE_THRESHOLD, make_summary
from kzp_lab06.errors import DataError
from kzp_lab06.loader import load_records
from kzp_lab06.reporting import format_report, write_report

EXIT_OK = 0
EXIT_DATA_ERROR = 1
EXIT_IO_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """Створює розбирач аргументів."""
    parser = argparse.ArgumentParser(prog="kzp-lab06", description="Звіт за реєстром студентів.")
    parser.add_argument("input", type=Path, help="вхідний CSV")
    parser.add_argument("output", type=Path, help="файл звіту")
    parser.add_argument(
        "--threshold",
        type=float,
        default=HIGH_AVERAGE_THRESHOLD,
        help="поріг відбору за середнім балом (типово 90)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Запускає програму й повертає код завершення (0 - успіх)."""
    args = build_parser().parse_args(argv)
    _use_utf8_streams()
    try:
        records = load_records(args.input)
        text = format_report(make_summary(records, args.threshold))
        write_report(args.output, text)
    except DataError as error:
        print(f"Помилка даних: {error}", file=sys.stderr)
        return EXIT_DATA_ERROR
    except OSError as error:
        print(f"Помилка запису звіту: {error}", file=sys.stderr)
        return EXIT_IO_ERROR
    print(text, end="")
    return EXIT_OK


def _use_utf8_streams() -> None:
    """Явно задає UTF-8 для stdout і stderr, щоб українські тексти не залежали від ОС."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
