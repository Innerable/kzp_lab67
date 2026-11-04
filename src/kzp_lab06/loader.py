"""Читання CSV та перетворення рядків на типізовані записи."""

import csv
from pathlib import Path

from kzp_lab06.errors import DataError

REQUIRED_COLUMNS = ("full_name", "group", "year", "average")
MIN_YEAR = 1
MAX_YEAR = 6
MAX_AVERAGE = 100.0

Record = dict[str, object]


def load_records(path: Path) -> list[Record]:
    """Читає CSV (UTF-8) і повертає записи зі встановленими типами.

    Файл лише із заголовком дає порожній список. Файл без заголовка або без
    обов'язкового стовпця викликає DataError.
    """
    try:
        # newline="" потрібен csv-модулю, щоб коректно читати перенесення всередині лапок.
        with path.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            _check_header(reader.fieldnames)
            # Нумерація з 2: перший фізичний рядок файлу містить заголовок.
            return [_parse_row(row, number) for number, row in enumerate(reader, start=2)]
    except (OSError, UnicodeDecodeError) as error:
        raise DataError(f"Не вдалося прочитати файл {path}: {error}") from error
    except csv.Error as error:
        raise DataError(f"Пошкоджений CSV {path}: {error}") from error


def _check_header(fieldnames: list[str] | None) -> None:
    """Перевіряє, що заголовок містить усі обов'язкові стовпці."""
    present = set(fieldnames or [])
    missing = [column for column in REQUIRED_COLUMNS if column not in present]
    if missing:
        raise DataError("Відсутні стовпці: " + ", ".join(missing))


def _parse_row(row: dict[str, str | None], number: int) -> Record:
    """Перетворює один рядок CSV на запис; помилка містить номер рядка й поле."""
    values: dict[str, str] = {}
    for column in REQUIRED_COLUMNS:
        value = row.get(column)
        if value is None or not value.strip():
            raise DataError(f"Рядок {number}: відсутнє значення поля {column}")
        values[column] = value.strip()

    year = _parse_number(int, values["year"], number, "year")
    average = _parse_number(float, values["average"], number, "average")
    if not MIN_YEAR <= year <= MAX_YEAR:
        raise DataError(f"Рядок {number}: поле year поза діапазоном {MIN_YEAR}-{MAX_YEAR}")
    if not 0.0 <= average <= MAX_AVERAGE:
        raise DataError(f"Рядок {number}: поле average поза діапазоном 0-{MAX_AVERAGE:.0f}")
    return {
        "full_name": values["full_name"],
        "group": values["group"],
        "year": year,
        "average": average,
    }


def _parse_number(kind: type, text: str, number: int, field: str):
    """Перетворює текст на число, зберігаючи першопричину помилки."""
    try:
        value = kind(text)
    except ValueError as error:
        raise DataError(f"Рядок {number}: поле {field} має хибний формат: {text!r}") from error
    if value != value:  # NaN
        raise DataError(f"Рядок {number}: поле {field} має бути числом")
    return value
