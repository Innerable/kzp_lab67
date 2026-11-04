"""Тести моделі лабораторної № 7."""

import dataclasses
import math

import pytest

from kzp_lab07.models import Bachelor, GroupRating, Learner, LearnerLike, Master, ReportSummary


def test_base_class_stores_and_trims():
    learner = Learner("  Іван  ", " КІ-301 ", 3, 80)
    assert (learner.full_name, learner.group, learner.year, learner.average) == (
        "Іван",
        "КІ-301",
        3,
        80.0,
    )


@pytest.mark.parametrize("value", [0, 0.0, 50, 100])
def test_average_setter_accepts_valid_and_boundary(value):
    learner = Learner("Іван", "КІ", 3, 10)
    learner.average = value
    assert learner.average == float(value)


@pytest.mark.parametrize("value", [-0.1, 100.01, math.nan])
def test_average_setter_rejects_invalid(value):
    learner = Learner("Іван", "КІ", 3, 10)
    with pytest.raises(ValueError, match="average"):
        learner.average = value
    assert learner.average == 10.0


@pytest.mark.parametrize("value", ["", "   ", None])
def test_text_setters_reject_blank(value):
    learner = Learner("Іван", "КІ", 3, 10)
    with pytest.raises(ValueError):
        learner.full_name = value
    with pytest.raises(ValueError):
        learner.group = value


@pytest.mark.parametrize("value", [0, 7, 2.5, True, "3"])
def test_year_setter_rejects_invalid(value):
    with pytest.raises(ValueError, match="year"):
        Learner("Іван", "КІ", value, 10)


def test_subtypes_restrict_year_ranges():
    assert Bachelor("А", "Г", 4, 50).year == 4
    assert Master("А", "Г", 5, 50).year == 5
    with pytest.raises(ValueError):
        Bachelor("А", "Г", 5, 50)
    with pytest.raises(ValueError):
        Master("А", "Г", 4, 50)


def test_subtypes_have_different_rating_formulas():
    assert Bachelor("А", "Г", 2, 80).rating() == pytest.approx(80.0)
    assert Master("А", "Г", 5, 80).rating() == pytest.approx(88.0)
    assert Learner("А", "Г", 2, 80).rating() == pytest.approx(80.0)


def test_str_and_repr():
    learner = Bachelor("Іван", "КІ-301", 3, 92.5)
    assert str(learner) == "Іван (КІ-301, курс 3, бал 92.50)"
    assert repr(learner) == "Bachelor(full_name='Іван', group='КІ-301', year=3, average=92.5)"


def test_equality_uses_type_name_and_group():
    first = Bachelor("Іван", "КІ-301", 3, 80)
    assert first == Bachelor("Іван", "КІ-301", 2, 99)
    assert first != Bachelor("Іван", "КІ-302", 3, 80)
    assert first != Learner("Іван", "КІ-301", 3, 80)
    assert first != "Іван"
    assert hash(first) == hash(Bachelor("Іван", "КІ-301", 1, 10))


def test_ordering_by_rating_desc_then_name():
    low = Bachelor("Б", "Г", 1, 70)
    high = Master("А", "Г", 5, 90)
    tie = Bachelor("А", "Г", 1, 70)
    assert sorted([low, high, tie]) == [high, tie, low]
    assert high < low
    with pytest.raises(TypeError):
        low < 5  # noqa: B015


def test_frozen_dataclass():
    rating = GroupRating("КІ", 2, 80.0)
    assert rating == GroupRating("КІ", 2, 80.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        rating.count = 3


def test_summary_dataclass_is_frozen_and_comparable():
    summary = ReportSummary(0, 90.0, 0, (), (), 0.0, None, None, None, ())
    assert summary == dataclasses.replace(summary)
    with pytest.raises(dataclasses.FrozenInstanceError):
        summary.count = 1


def test_learner_satisfies_protocol():
    assert isinstance(Bachelor("А", "Г", 1, 50), LearnerLike)
    assert not isinstance(object(), LearnerLike)
