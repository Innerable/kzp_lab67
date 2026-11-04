"""Тести loader лабораторної № 6."""

from pathlib import Path

import pytest
from conftest import DATA_FILE, HEADER

from kzp_lab06.errors import DataError
from kzp_lab06.loader import load_records


def test_loads_typed_records(write_csv):
    path = write_csv(HEADER + "Петренко Іван,КІ-301,3,92.5\n")
    assert load_records(path) == [
        {"full_name": "Петренко Іван", "group": "КІ-301", "year": 3, "average": 92.5}
    ]


def test_sample_file_has_eight_records():
    assert len(load_records(DATA_FILE)) == 8


def test_header_only_gives_empty_list(write_csv):
    assert load_records(write_csv(HEADER)) == []


def test_quoted_comma_in_name(write_csv):
    path = write_csv(HEADER + '"Шевченко, Тарас",КІ-302,2,95\n')
    assert load_records(path)[0]["full_name"] == "Шевченко, Тарас"


def test_duplicates_are_kept(write_csv):
    row = "Іван,КІ-301,3,80\n"
    assert len(load_records(write_csv(HEADER + row + row))) == 2


@pytest.mark.parametrize("average", ["0", "100"])
def test_boundary_averages_are_accepted(write_csv, average):
    assert load_records(write_csv(HEADER + f"Іван,КІ-301,3,{average}\n"))[0]["average"] in (0, 100)


def test_missing_column_names_the_column(write_csv):
    with pytest.raises(DataError, match="average"):
        load_records(write_csv("full_name,group,year\nІван,КІ-301,3\n"))


def test_empty_file_is_an_error(write_csv):
    with pytest.raises(DataError, match="Відсутні стовпці"):
        load_records(write_csv(""))


def test_bad_number_has_line_field_and_cause(write_csv):
    path = write_csv(HEADER + "Іван,КІ-301,3,80\nМарія,КІ-301,3,abc\n")
    with pytest.raises(DataError, match="Рядок 3.*average") as info:
        load_records(path)
    assert isinstance(info.value.__cause__, ValueError)


def test_missing_value_in_short_row(write_csv):
    with pytest.raises(DataError, match="Рядок 2.*average"):
        load_records(write_csv(HEADER + "Іван,КІ-301,3\n"))


def test_empty_value_is_rejected(write_csv):
    with pytest.raises(DataError, match="Рядок 2.*group"):
        load_records(write_csv(HEADER + "Іван,,3,80\n"))


@pytest.mark.parametrize(
    "row",
    ["Іван,КІ-301,3,-1", "Іван,КІ-301,3,100.5", "Іван,КІ-301,0,80", "Іван,КІ-301,7,80"],
)
def test_out_of_range_values(write_csv, row):
    with pytest.raises(DataError, match="поза діапазоном"):
        load_records(write_csv(HEADER + row + "\n"))


def test_nan_is_rejected(write_csv):
    with pytest.raises(DataError, match="average"):
        load_records(write_csv(HEADER + "Іван,КІ-301,3,nan\n"))


def test_missing_file_keeps_cause(tmp_path: Path):
    with pytest.raises(DataError, match="Не вдалося прочитати") as info:
        load_records(tmp_path / "missing.csv")
    assert isinstance(info.value.__cause__, OSError)


def test_invalid_utf8_is_data_error(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_bytes(b"\xff\xfe\x00bad")
    with pytest.raises(DataError):
        load_records(path)
