"""Читання CSV і створення об'єктів Learner."""

import csv
from pathlib import Path

from kzp_lab07.errors import DataError
from kzp_lab07.models import Bachelor, Learner, Master

REQUIRED_COLUMNS = ("full_name", "group", "year", "average")
LAST_BACHELOR_YEAR = Bachelor.YEAR_RANGE[1]


def create_learner(full_name: str, group: str, year: int, average: float) -> Learner:
    """Фабрика: єдине місце, де тип обирається за курсом."""
    kind = Bachelor if year <= LAST_BACHELOR_YEAR else Master
    return kind(full_name, group, year, average)


def load_learners(path: Path) -> list[Learner]:
    """Читає CSV (UTF-8) і повертає об'єкти Learner; файл лише із заголовком дає []."""
    try:
        with path.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                raise DataError("Відсутні стовпці: " + ", ".join(missing))
            return [_parse_row(row, number) for number, row in enumerate(reader, start=2)]
    except (OSError, UnicodeDecodeError) as error:
        raise DataError(f"Не вдалося прочитати файл {path}: {error}") from error
    except csv.Error as error:
        raise DataError(f"Пошкоджений CSV {path}: {error}") from error


def _parse_row(row: dict[str, str | None], number: int) -> Learner:
    """Створює Learner з рядка; помилка містить номер рядка та першопричину."""
    values: dict[str, str] = {}
    for column in REQUIRED_COLUMNS:
        value = row.get(column)
        if value is None or not value.strip():
            raise DataError(f"Рядок {number}: відсутнє значення поля {column}")
        values[column] = value.strip()
    try:
        year = int(values["year"])
        average = float(values["average"])
    except ValueError as error:
        raise DataError(f"Рядок {number}: числове поле має хибний формат") from error
    try:
        return create_learner(values["full_name"], values["group"], year, average)
    except ValueError as error:
        raise DataError(f"Рядок {number}: {error}") from error
