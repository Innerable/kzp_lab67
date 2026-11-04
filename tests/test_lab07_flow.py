"""Тести loader, analysis, CLI лабораторної № 7 і сумісності зі звітом лабораторної № 6."""

import io
import sys

import pytest
from conftest import DATA_FILE, HEADER

from kzp_lab06 import cli as cli06
from kzp_lab07.analysis import group_ratings, make_summary, select_high
from kzp_lab07.cli import main
from kzp_lab07.errors import DataError
from kzp_lab07.loader import create_learner, load_learners
from kzp_lab07.models import Bachelor, Master
from kzp_lab07.reporting import format_report


class DuckLearner:
    """Не є підкласом Learner: аналіз має працювати за контрактом, а не за типом."""

    full_name = "Качка"
    group = "ДУ-1"
    year = 1
    average = 95.0

    def rating(self) -> float:
        return 1000.0


def test_factory_chooses_subtype_by_year_boundary():
    assert type(create_learner("А", "Г", 4, 50)) is Bachelor
    assert type(create_learner("А", "Г", 5, 50)) is Master


def test_loader_builds_both_subtypes():
    learners = load_learners(DATA_FILE)
    assert len(learners) == 8
    assert {type(learner) for learner in learners} == {Bachelor, Master}


def test_loader_header_only_is_empty(write_csv):
    assert load_learners(write_csv(HEADER)) == []


def test_loader_quoted_comma_and_duplicates(write_csv):
    row = '"Шевченко, Тарас",КІ-302,2,95\n'
    learners = load_learners(write_csv(HEADER + row + row))
    assert [learner.full_name for learner in learners] == ["Шевченко, Тарас"] * 2


def test_loader_error_has_line_and_cause(write_csv):
    path = write_csv(HEADER + "Іван,КІ-301,3,80\nМарія,КІ-301,3,150\n")
    with pytest.raises(DataError, match="Рядок 3") as info:
        load_learners(path)
    assert isinstance(info.value.__cause__, ValueError)


def test_loader_missing_column_and_value(write_csv):
    with pytest.raises(DataError, match="Відсутні стовпці"):
        load_learners(write_csv("full_name,group\nА,Б\n"))
    with pytest.raises(DataError, match="Рядок 2"):
        load_learners(write_csv(HEADER + "Іван,КІ-301,3\n"))
    with pytest.raises(DataError, match="хибний формат"):
        load_learners(write_csv(HEADER + "Іван,КІ-301,x,80\n"))


def test_loader_missing_file(tmp_path):
    with pytest.raises(DataError, match="Не вдалося прочитати"):
        load_learners(tmp_path / "none.csv")


def test_analysis_works_with_duck_typed_objects():
    summary = make_summary([DuckLearner()])
    assert summary.best_name == "Качка"
    assert summary.group_ratings[0].mean_rating == 1000.0
    assert len(select_high([DuckLearner()])) == 1


def test_group_ratings_use_subtype_weights():
    ratings = group_ratings([Bachelor("А", "Г", 1, 80), Master("Б", "Г", 5, 80)])
    assert ratings[0].mean_rating == pytest.approx(84.0)


def test_empty_summary():
    summary = make_summary([])
    assert summary.count == 0 and summary.best_name is None and summary.group_ratings == ()
    assert "Найкращий результат: немає даних" in format_report(summary)


def test_report_matches_lab06_on_same_csv(tmp_path):
    old, new = tmp_path / "old.txt", tmp_path / "new.txt"
    assert cli06.main([str(DATA_FILE), str(old)]) == 0
    assert main([str(DATA_FILE), str(new)]) == 0
    assert old.read_bytes() == new.read_bytes()


def test_ratings_flag_appends_section(tmp_path):
    output = tmp_path / "r.txt"
    assert main([str(DATA_FILE), str(output), "--ratings"]) == 0
    text = output.read_text(encoding="utf-8")
    assert "Рейтинг груп:\n  КІ-301: 90.25" in text
    assert "  КІ-501: 103.68" in text


def test_cli_error_codes(write_csv, tmp_path, capsys):
    bad = write_csv(HEADER + "Іван,КІ-301,3,abc\n")
    assert main([str(bad), str(tmp_path / "r.txt")]) == 1
    assert "Рядок 2" in capsys.readouterr().err
    blocker = tmp_path / "file"
    blocker.write_text("x", encoding="utf-8")
    assert main([str(DATA_FILE), str(blocker / "r.txt")]) == 2


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as info:
        main(["--version"])
    assert info.value.code == 0
    assert capsys.readouterr().out.startswith("kzp-lab07 ")


def test_stdout_uses_lf_even_if_platform_default_is_crlf(tmp_path, monkeypatch):
    raw = io.BytesIO()
    stream = io.TextIOWrapper(raw, encoding="cp1252", newline="\r\n", write_through=True)
    monkeypatch.setattr(sys, "stdout", stream)
    output = tmp_path / "report.txt"
    assert main([str(DATA_FILE), str(output)]) == 0
    assert raw.getvalue() == output.read_bytes()
