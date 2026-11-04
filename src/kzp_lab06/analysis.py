"""Обчислення над записами: відбір, агрегування, унікальні значення."""

from kzp_lab06.loader import Record

HIGH_AVERAGE_THRESHOLD = 90.0
NUMERIC_FIELDS = frozenset({"year", "average"})


def select_high(records: list[Record], threshold: float = HIGH_AVERAGE_THRESHOLD) -> list[Record]:
    """Повертає записи, у яких середній бал не нижчий за поріг."""
    return [record for record in records if float(record["average"]) >= threshold]


def count_by_group(records: list[Record]) -> dict[str, int]:
    """Рахує записи за групою; ключі йдуть у стабільному (алфавітному) порядку."""
    counts: dict[str, int] = {}
    for record in records:
        group = str(record["group"])
        counts[group] = counts.get(group, 0) + 1
    return {group: counts[group] for group in sorted(counts)}


def unique_groups(records: list[Record]) -> set[str]:
    """Повертає множину унікальних груп."""
    return {str(record["group"]) for record in records}


def mean_average(records: list[Record]) -> float:
    """Повертає середній бал; для порожнього списку - 0.0."""
    if not records:
        return 0.0
    return sum(float(record["average"]) for record in records) / len(records)


def best_record(records: list[Record]) -> Record | None:
    """Повертає запис із найвищим балом (за рівності - перший за ПІБ) або None."""
    if not records:
        return None
    return min(records, key=lambda record: (-float(record["average"]), str(record["full_name"])))


def summarize(
    records: list[Record],
    *metrics: str,
    minimum_average: float = 0.0,
    **labels: str,
) -> dict[str, object]:
    """Сумує вибрані числові поля для записів із балом не нижче minimum_average.

    metrics - назви полів (year, average), labels - підписи результатів за назвою поля.
    Невідому назву поля відхиляє ValueError.
    """
    for metric in metrics:
        if metric not in NUMERIC_FIELDS:
            raise ValueError(f"Невідома метрика: {metric}")
    selected = [record for record in records if float(record["average"]) >= minimum_average]
    result: dict[str, object] = {"count": len(selected)}
    for metric in metrics:
        result[labels.get(metric, metric)] = sum(float(record[metric]) for record in selected)
    return result


def make_summary(
    records: list[Record], threshold: float = HIGH_AVERAGE_THRESHOLD
) -> dict[str, object]:
    """Збирає дані для звіту: кількість, відбір, групи, середній бал, найкращий запис."""
    return {
        "count": len(records),
        "threshold": threshold,
        "selected": len(select_high(records, threshold)),
        "groups": sorted(unique_groups(records)),
        "group_counts": count_by_group(records),
        "mean_average": mean_average(records),
        "best": best_record(records),
    }
