"""Тести analysis і reporting лабораторної № 6."""

import pytest

from kzp_lab06.analysis import (
    best_record,
    count_by_group,
    make_summary,
    mean_average,
    select_high,
    summarize,
    unique_groups,
)
from kzp_lab06.reporting import format_report, write_report


def rec(name, group, average, year=3):
    return {"full_name": name, "group": group, "year": year, "average": average}


RECORDS = [rec("Б", "КІ-2", 90.0), rec("А", "КІ-1", 89.99), rec("В", "КІ-2", 95.0)]


def test_select_includes_threshold_and_excludes_below():
    assert [r["full_name"] for r in select_high(RECORDS)] == ["Б", "В"]


def test_select_custom_threshold():
    assert len(select_high(RECORDS, 95.0)) == 1


def test_count_by_group_is_sorted():
    assert list(count_by_group(RECORDS).items()) == [("КІ-1", 1), ("КІ-2", 2)]


def test_unique_groups_is_a_set():
    assert unique_groups(RECORDS + RECORDS) == {"КІ-1", "КІ-2"}


def test_mean_and_best():
    assert mean_average(RECORDS) == pytest.approx((90.0 + 89.99 + 95.0) / 3)
    assert best_record(RECORDS)["full_name"] == "В"


def test_best_tie_is_resolved_by_name():
    assert best_record([rec("Я", "А", 90.0), rec("Б", "А", 90.0)])["full_name"] == "Б"


def test_empty_input():
    assert select_high([]) == []
    assert count_by_group([]) == {}
    assert mean_average([]) == 0.0
    assert best_record([]) is None


def test_summarize_with_args_default_and_kwargs():
    result = summarize(RECORDS, "average", "year", minimum_average=90.0, average="Сума")
    assert result == {"count": 2, "Сума": 185.0, "year": 6.0}


def test_summarize_default_minimum_keeps_all():
    assert summarize(RECORDS, "year") == {"count": 3, "year": 9.0}


def test_summarize_unknown_metric():
    with pytest.raises(ValueError, match="Невідома метрика"):
        summarize(RECORDS, "salary")


def test_summarize_all_filtered_gives_zero():
    assert summarize(RECORDS, "average", minimum_average=100.0) == {"count": 0, "average": 0.0}


def test_report_text_is_exact():
    expected = (
        "Записів: 3\n"
        "Відібрано (середній бал >= 90.0): 2\n"
        "Групи: КІ-1, КІ-2\n"
        "Кількість за групою:\n"
        "  КІ-1: 1\n"
        "  КІ-2: 2\n"
        "Середній бал: 91.66\n"
        "Найкращий результат: В (КІ-2) — 95.00\n"
    )
    assert format_report(make_summary(RECORDS)) == expected


def test_report_for_empty_input():
    text = format_report(make_summary([]))
    assert "Записів: 0" in text
    assert "Групи: немає" in text
    assert text.endswith("Найкращий результат: немає даних\n")


def test_write_report_creates_directory_and_uses_utf8(tmp_path):
    target = tmp_path / "nested" / "report.txt"
    write_report(target, "Готово — так\n")
    assert target.read_bytes() == "Готово — так\n".encode()
