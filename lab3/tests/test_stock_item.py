from datetime import date

import pytest

from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InvalidDataError
from restaurant.inventory.stock_item import StockItem


def test_quantity_must_be_positive(milk: Ingredient, today: date) -> None:
    with pytest.raises(InvalidDataError):
        StockItem(milk, 0, today)


def test_expiry_logic(milk: Ingredient, today: date) -> None:
    item = StockItem(milk, 1000, today)
    assert item.expiry_date() == date(2026, 11, 28)
    assert not item.is_expired(date(2026, 11, 28))
    assert item.is_expired(date(2026, 11, 29))
    assert item.days_until_expiry(today) == 7


def test_consume_takes_at_most_what_is_left(milk: Ingredient, today: date) -> None:
    item = StockItem(milk, 100, today)
    assert item.consume(30) == 30
    assert item.consume(500) == 70
    assert item.is_empty()
