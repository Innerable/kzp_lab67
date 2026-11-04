"""Формування та запис текстового звіту."""

from pathlib import Path


def format_report(summary: dict[str, object]) -> str:
    """Форматує підсумок у детермінований текстовий звіт."""
    lines = [
        f"Записів: {summary['count']}",
        f"Відібрано (середній бал >= {float(summary['threshold']):.1f}): {summary['selected']}",
        "Групи: " + (", ".join(summary["groups"]) or "немає"),
        "Кількість за групою:",
    ]
    lines += [f"  {group}: {count}" for group, count in summary["group_counts"].items()]
    lines.append(f"Середній бал: {float(summary['mean_average']):.2f}")
    best = summary["best"]
    if best is None:
        lines.append("Найкращий результат: немає даних")
    else:
        lines.append(
            f"Найкращий результат: {best['full_name']} ({best['group']}) — "
            f"{float(best['average']):.2f}"
        )
    return "\n".join(lines) + "\n"


def write_report(path: Path, text: str) -> None:
    """Записує звіт у файл UTF-8, створюючи відсутні каталоги."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # with гарантує закриття файла навіть у разі помилки запису.
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(text)
