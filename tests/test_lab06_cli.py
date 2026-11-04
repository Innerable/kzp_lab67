"""Тести CLI лабораторної № 6."""

from conftest import DATA_FILE, HEADER

from kzp_lab06.cli import main


def test_success_writes_report_and_returns_zero(tmp_path, capsys):
    output = tmp_path / "out" / "report.txt"
    assert main([str(DATA_FILE), str(output)]) == 0
    text = output.read_text(encoding="utf-8")
    assert "Записів: 8" in text
    assert capsys.readouterr().out == text


def test_custom_threshold(tmp_path):
    output = tmp_path / "r.txt"
    assert main([str(DATA_FILE), str(output), "--threshold", "95"]) == 0
    assert "Відібрано (середній бал >= 95.0): 2" in output.read_text(encoding="utf-8")


def test_bad_csv_returns_nonzero_and_writes_no_report(write_csv, tmp_path, capsys):
    bad = write_csv(HEADER + "Іван,КІ-301,3,abc\n")
    output = tmp_path / "report.txt"
    assert main([str(bad), str(output)]) == 1
    assert "Рядок 2" in capsys.readouterr().err
    assert not output.exists()


def test_missing_input_returns_nonzero(tmp_path, capsys):
    assert main([str(tmp_path / "none.csv"), str(tmp_path / "r.txt")]) == 1
    assert "Помилка даних" in capsys.readouterr().err


def test_unwritable_output_returns_io_code(tmp_path, capsys):
    blocker = tmp_path / "file"
    blocker.write_text("x", encoding="utf-8")
    assert main([str(DATA_FILE), str(blocker / "report.txt")]) == 2
    assert "Помилка запису" in capsys.readouterr().err
