"""Предметна модель: Learner, підтипи Bachelor і Master, протокол та підсумок."""

import math
from dataclasses import dataclass
from typing import ClassVar, Protocol, runtime_checkable

MAX_AVERAGE = 100.0


@runtime_checkable
class LearnerLike(Protocol):
    """Спільний контракт для аналізу: дані студента та операція rating()."""

    @property
    def full_name(self) -> str: ...

    @property
    def group(self) -> str: ...

    @property
    def year(self) -> int: ...

    @property
    def average(self) -> float: ...

    def rating(self) -> float: ...


class Learner:
    """Базовий студент реєстру з перевіркою полів у setter-ах.

    Допустимий діапазон курсів задає атрибут класу YEAR_RANGE, а вагу рейтингу - WEIGHT,
    тому підтипи відрізняються даними, а не розгалуженнями.
    """

    YEAR_RANGE: ClassVar[tuple[int, int]] = (1, 6)
    WEIGHT: ClassVar[float] = 1.0

    def __init__(self, full_name: str, group: str, year: int, average: float) -> None:
        """Створює студента; хибні значення відхиляє ValueError."""
        self.full_name = full_name
        self.group = group
        self.year = year
        self.average = average

    @property
    def full_name(self) -> str:
        """ПІБ (непорожній рядок без крайніх пробілів)."""
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        self._full_name = self._check_text(value, "full_name")

    @property
    def group(self) -> str:
        """Назва групи (непорожній рядок без крайніх пробілів)."""
        return self._group

    @group.setter
    def group(self, value: str) -> None:
        self._group = self._check_text(value, "group")

    @property
    def year(self) -> int:
        """Курс у межах YEAR_RANGE свого типу."""
        return self._year

    @year.setter
    def year(self, value: int) -> None:
        low, high = self.YEAR_RANGE
        if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
            raise ValueError(f"year має бути цілим числом {low}-{high}: {value!r}")
        self._year = value

    @property
    def average(self) -> float:
        """Середній бал від 0 до 100 включно."""
        return self._average

    @average.setter
    def average(self, value: float) -> None:
        number = float(value)
        if math.isnan(number) or not 0.0 <= number <= MAX_AVERAGE:
            raise ValueError(f"average має бути числом 0-{MAX_AVERAGE:.0f}: {value!r}")
        self._average = number

    def rating(self) -> float:
        """Повертає рейтинг: середній бал, помножений на вагу типу."""
        return self.average * self.WEIGHT

    @property
    def sort_key(self) -> tuple[float, str]:
        """Ключ впорядкування: рейтинг за спаданням, потім ПІБ."""
        return (-self.rating(), self.full_name)

    @staticmethod
    def _check_text(value: str, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} не може бути порожнім")
        return value.strip()

    def __str__(self) -> str:
        return f"{self.full_name} ({self.group}, курс {self.year}, бал {self.average:.2f})"

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(full_name={self.full_name!r}, group={self.group!r}, "
            f"year={self.year!r}, average={self.average!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Студенти рівні, якщо збігаються тип, ПІБ і група (ключ round-trip)."""
        if not isinstance(other, Learner):
            return NotImplemented
        mine = (type(self), self.full_name, self.group)
        return mine == (type(other), other.full_name, other.group)

    def __hash__(self) -> int:
        return hash((type(self), self.full_name, self.group))

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Learner):
            return NotImplemented
        return self.sort_key < other.sort_key


class Bachelor(Learner):
    """Студент бакалаврату (курси 1-4), рейтинг без надбавки."""

    YEAR_RANGE = (1, 4)
    WEIGHT = 1.0


class Master(Learner):
    """Студент магістратури (курси 5-6), рейтинг із коефіцієнтом 1.1."""

    YEAR_RANGE = (5, 6)
    WEIGHT = 1.1


@dataclass(frozen=True)
class GroupRating:
    """Середній рейтинг однієї групи."""

    group: str
    count: int
    mean_rating: float


@dataclass(frozen=True)
class ReportSummary:
    """Незмінний підсумок для звіту."""

    count: int
    threshold: float
    selected: int
    groups: tuple[str, ...]
    group_counts: tuple[tuple[str, int], ...]
    mean_average: float
    best_name: str | None
    best_group: str | None
    best_average: float | None
    group_ratings: tuple[GroupRating, ...]
