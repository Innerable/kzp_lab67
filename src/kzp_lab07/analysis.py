"""Обчислення над об'єктами через спільний контракт LearnerLike (без перевірки типів)."""

from collections.abc import Sequence

from kzp_lab07.models import GroupRating, LearnerLike, ReportSummary

HIGH_AVERAGE_THRESHOLD = 90.0


def select_high(
    learners: Sequence[LearnerLike], threshold: float = HIGH_AVERAGE_THRESHOLD
) -> list[LearnerLike]:
    """Повертає студентів із середнім балом не нижче порога."""
    return [learner for learner in learners if learner.average >= threshold]


def count_by_group(learners: Sequence[LearnerLike]) -> dict[str, int]:
    """Рахує студентів за групою у стабільному порядку."""
    counts: dict[str, int] = {}
    for learner in learners:
        counts[learner.group] = counts.get(learner.group, 0) + 1
    return {group: counts[group] for group in sorted(counts)}


def best_learner(learners: Sequence[LearnerLike]) -> LearnerLike | None:
    """Повертає студента з найвищим балом (за рівності - за ПІБ) або None."""
    if not learners:
        return None
    return min(learners, key=lambda learner: (-learner.average, learner.full_name))


def group_ratings(learners: Sequence[LearnerLike]) -> tuple[GroupRating, ...]:
    """Рахує середній рейтинг груп; rating() поліморфний, тип студента не перевіряється."""
    totals: dict[str, list[float]] = {}
    for learner in learners:
        totals.setdefault(learner.group, []).append(learner.rating())
    return tuple(
        GroupRating(group, len(values), sum(values) / len(values))
        for group, values in sorted(totals.items())
    )


def make_summary(
    learners: Sequence[LearnerLike], threshold: float = HIGH_AVERAGE_THRESHOLD
) -> ReportSummary:
    """Збирає незмінний підсумок для звіту."""
    best = best_learner(learners)
    counts = count_by_group(learners)
    mean = sum(learner.average for learner in learners) / len(learners) if learners else 0.0
    return ReportSummary(
        count=len(learners),
        threshold=threshold,
        selected=len(select_high(learners, threshold)),
        groups=tuple(counts),
        group_counts=tuple(counts.items()),
        mean_average=mean,
        best_name=best.full_name if best else None,
        best_group=best.group if best else None,
        best_average=best.average if best else None,
        group_ratings=group_ratings(learners),
    )
