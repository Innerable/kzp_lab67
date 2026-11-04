"""Спільні фікстури тестів."""

from pathlib import Path

import pytest

HEADER = "full_name,group,year,average\n"
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "input.csv"


@pytest.fixture
def write_csv(tmp_path: Path):
    """Повертає функцію, що записує CSV (UTF-8) у тимчасовий каталог."""

    def _write(text: str, name: str = "input.csv") -> Path:
        path = tmp_path / name
        path.write_text(text, encoding="utf-8", newline="")
        return path

    return _write
