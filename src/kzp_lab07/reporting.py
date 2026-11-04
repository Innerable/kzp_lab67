"""Формування та запис текстового звіту (формат лабораторної № 6 збережено)."""

from pathlib import Path

from kzp_lab07.models import ReportSummary


def format_report(summary: ReportSummary, include_ratings: bool = False) -> str:
    """Форматує підсумок; основні рядки збігаються зі звітом лабораторної № 6."""
    lines = [
        f"Записів: {summary.count}",
        f"Відібрано (середній бал >= {summary.threshold:.1f}): {summary.selected}",
        "Групи: " + (", ".join(summary.groups) or "немає"),
        "Кількість за групою:",
    ]
    lines += [f"  {group}: {count}" for group, count in summary.group_counts]
    lines.append(f"Середній бал: {summary.mean_average:.2f}")
    if summary.best_name is None:
        lines.append("Найкращий результат: немає даних")
    else:
        lines.append(
            f"Найкращий результат: {summary.best_name} ({summary.best_group}) — "
            f"{summary.best_average:.2f}"
        )
    if include_ratings:
        lines.append("Рейтинг груп:")
        lines += [f"  {item.group}: {item.mean_rating:.2f}" for item in summary.group_ratings]
    return "\n".join(lines) + "\n"


def write_report(path: Path, text: str) -> None:
    """Записує звіт у файл UTF-8, створюючи відсутні каталоги."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(text)
