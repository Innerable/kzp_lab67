# kzp_lab67 — лабораторна робота № 6 (Python)

Курс «Кросплатформні засоби програмування». **Варіант 6 — реєстр студентів.**
Пакет `kzp_lab06`: CSV → словники, списки, множини, comprehensions, текстовий звіт.
Звіт: [REPORT06.md](REPORT06.md).

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
```

Після встановлення доступна команда `kzp-lab06`.
Коди завершення: `0` — успіх, `1` — помилка даних (повідомлення в stderr), `2` — помилка запису звіту.

## Перевірки

```bash
python -m pytest
ruff check .
ruff format --check .
python -m build
```

### Перевірка wheel у чистому середовищі

```bash
python -m venv .venv-wheel
.venv-wheel/bin/python -m pip install --no-deps dist/*.whl     # Windows: .venv-wheel\Scripts\python
.venv-wheel/bin/python -m kzp_lab06.cli data/input.csv reports/wheel-summary.txt
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) на Ubuntu: `ruff check`, `ruff format --check`,
`pytest`, збирання wheel, установлення wheel у чисте середовище та запуск CLI.
