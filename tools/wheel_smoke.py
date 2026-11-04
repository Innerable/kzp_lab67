"""Перевіряє зібраний wheel у чистому середовищі: успішний і помилковий сценарії CLI.

Працює однаково на Linux, macOS і Windows. Запуск з кореня репозиторію:
    python tools/wheel_smoke.py
"""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(python: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    """Запускає python із чистого середовища; вивід читається як UTF-8 байти."""
    return subprocess.run([str(python), *args], capture_output=True, check=False)


def text(data: bytes) -> str:
    """Декодує вивід CLI (UTF-8 на всіх ОС)."""
    return data.decode("utf-8")


def check(condition: bool, message: str) -> None:
    """Зупиняє перевірку з поясненням, якщо умова не виконується."""
    if not condition:
        sys.exit(f"FAIL: {message}")
    print(f"ok: {message}")


def use_utf8_output() -> None:
    """Перемикає stdout і stderr на UTF-8: на Windows типове кодування (cp1252) не має кирилиці."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def main() -> None:
    use_utf8_output()
    wheels = sorted((ROOT / "dist").glob("*.whl"))
    check(len(wheels) == 1, f"у dist/ рівно один wheel ({[w.name for w in wheels]})")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        env_dir = work / "env"
        venv.create(env_dir, with_pip=True)
        scripts = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
        python = scripts / ("python.exe" if sys.platform == "win32" else "python")

        install = run(python, "-m", "pip", "install", "--no-deps", str(wheels[0]))
        check(install.returncode == 0, "wheel встановлено без dev-залежностей")

        data = ROOT / "data" / "input.csv"
        bad_csv = work / "bad.csv"
        bad_csv.write_text("full_name,group,year,average\nІван,КІ-301,3,abc\n", encoding="utf-8")

        reports = {}
        for number in ("06", "07"):
            module = f"kzp_lab{number}.cli"
            label = f"лаб. {number}"
            version = run(python, "-m", module, "--version")
            check(
                version.returncode == 0 and f"kzp-lab{number}" in text(version.stdout),
                f"{label}: --version",
            )

            good = work / f"report{number}.txt"
            ok = run(python, "-m", module, str(data), str(good))
            check(ok.returncode == 0, f"{label}: успішний сценарій, код 0")
            report = good.read_text(encoding="utf-8")
            check("Записів: 8" in report, f"{label}: звіт містить очікувані дані")
            check(text(ok.stdout) == report, f"{label}: stdout збігається з файлом звіту")
            reports[number] = report

            bad_report = work / f"bad-report{number}.txt"
            failed = run(python, "-m", module, str(bad_csv), str(bad_report))
            check(failed.returncode == 1, f"{label}: помилковий сценарій, код 1")
            check("Рядок 2" in text(failed.stderr), f"{label}: у помилці є номер рядка")
            check(not bad_report.exists(), f"{label}: звіт не створюється для пошкодженого CSV")

            script = scripts / (f"kzp-lab{number}" + (".exe" if sys.platform == "win32" else ""))
            check(script.exists(), f"{label}: встановлено команду kzp-lab{number}")

        check(reports["06"] == reports["07"], "звіт лаб. 7 збігається зі звітом лаб. 6")
        rated = work / "rated.txt"
        run(python, "-m", "kzp_lab07.cli", str(data), str(rated), "--ratings")
        check("Рейтинг груп:" in rated.read_text(encoding="utf-8"), "лаб. 07: --ratings")


if __name__ == "__main__":
    main()
