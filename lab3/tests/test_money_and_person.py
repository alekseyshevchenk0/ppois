from datetime import date
from decimal import Decimal

import pytest

from restaurant.exceptions import InvalidDataError
from restaurant.money import apply_percent, percent_of
from restaurant.person import Person


def test_apply_percent_rounds_to_cents() -> None:
    assert apply_percent(Decimal("7.50"), Decimal(10)) == Decimal("8.25")
    assert apply_percent(Decimal("7.50"), Decimal(-50)) == Decimal("3.75")


def test_percent_of() -> None:
    assert percent_of(Decimal("200"), Decimal("12.5")) == Decimal("25.00")


def test_person_validation() -> None:
    with pytest.raises(InvalidDataError):
        Person("", "123", date(1990, 1, 1))
    with pytest.raises(InvalidDataError):
        Person("Ann", " ", date(1990, 1, 1))


def test_age_depends_on_birthday() -> None:
    person = Person("Ann", "123", date(1990, 5, 17))
    assert person.age_on(date(2026, 5, 16)) == 35
    assert person.age_on(date(2026, 5, 17)) == 36


def test_is_adult() -> None:
    person = Person("Ann", "123", date(2008, 6, 1))
    assert not person.is_adult(date(2026, 5, 31))
    assert person.is_adult(date(2026, 6, 1))


def test_matches_ignores_case_and_spaces() -> None:
    assert Person("Anna Petrova", "123", date(1990, 1, 1)).matches("  petrov ")
    assert not Person("Anna", "123", date(1990, 1, 1)).matches("bob")
