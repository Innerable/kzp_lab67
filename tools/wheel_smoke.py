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


def main() -> None:
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

        version = run(python, "-m", "kzp_lab06.cli", "--version")
        check(version.returncode == 0 and "kzp-lab06" in text(version.stdout), "--version")

        good = work / "report.txt"
        ok = run(python, "-m", "kzp_lab06.cli", str(ROOT / "data" / "input.csv"), str(good))
        check(ok.returncode == 0, "успішний сценарій: код 0")
        report = good.read_text(encoding="utf-8")
        check("Записів: 8" in report, "звіт містить очікувані дані")
        check(text(ok.stdout) == report, "stdout збігається з файлом звіту")

        bad_csv = work / "bad.csv"
        bad_csv.write_text("full_name,group,year,average\nІван,КІ-301,3,abc\n", encoding="utf-8")
        bad_report = work / "bad-report.txt"
        failed = run(python, "-m", "kzp_lab06.cli", str(bad_csv), str(bad_report))
        check(failed.returncode == 1, "помилковий сценарій: код 1")
        check("Рядок 2" in text(failed.stderr), "повідомлення про помилку містить номер рядка")
        check(not bad_report.exists(), "звіт не створюється для пошкодженого CSV")

        script = scripts / ("kzp-lab06.exe" if sys.platform == "win32" else "kzp-lab06")
        check(script.exists(), "встановлено консольну команду kzp-lab06")


if __name__ == "__main__":
    main()
