# kzp_lab67 — лабораторні роботи № 6–7 (Python)

Курс «Кросплатформні засоби програмування». **Варіант 6 — реєстр студентів.**

| Пакет | Лабораторна | Суть | Звіт |
|---|---|---|---|
| `kzp_lab06` | № 6 | CSV → словники, списки, множини, comprehensions, текстовий звіт | [REPORT06.md](REPORT06.md) |
| `kzp_lab07` | № 7 | ті самі дані як об'єкти: `Learner`, `Bachelor`, `Master`, `dataclass`, `Protocol` | [REPORT07.md](REPORT07.md) |

## Формат CSV

UTF-8, кома як роздільник, перший рядок — заголовок:

```csv
full_name,group,year,average
Петренко Іван,КІ-301,3,92.5
"Шевченко, Тарас",КІ-302,2,95.0
```

`year` — ціле 1–6, `average` — число 0–100. Поле з комою беруть у лапки.
Файл лише із заголовком — коректний порожній набір; без обов'язкового стовпця — помилка.

## Встановлення

Потрібен Python 3.11 або новіший.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Запуск

```bash
python -m kzp_lab06.cli data/input.csv reports/summary-lab06.txt
python -m kzp_lab07.cli data/input.csv reports/summary-lab07.txt --ratings
```

Після встановлення доступні команди `kzp-lab06` і `kzp-lab07` (`--version` друкує версію).
Коди завершення: `0` — успіх, `1` — помилка даних (повідомлення в stderr), `2` — помилка запису звіту.

## Перевірки

```bash
python -m pytest
ruff check .
ruff format --check .
python -m build
python tools/wheel_smoke.py   # wheel у чистому середовищі: успішний і помилковий сценарії
```

### Перевірка wheel у чистому середовищі

```bash
python -m venv .venv-wheel
.venv-wheel/bin/python -m pip install --no-deps dist/*.whl     # Windows: .venv-wheel\Scripts\python
.venv-wheel/bin/python -m kzp_lab06.cli data/input.csv reports/wheel-summary.txt
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) запускається на **Ubuntu, Windows і macOS**.
Кожен запуск виконує `ruff check`, `ruff format --check`, `pytest`, збирає wheel,
перевіряє його в чистому середовищі (`tools/wheel_smoke.py`: для обох CLI успішний сценарій із кодом 0
і помилковий із кодом 1; звіт лаб. 7 порівнюється зі звітом лаб. 6) та публікує wheel як артефакт `wheel-<ОС>-<номер запуску>`.
оновити CI
