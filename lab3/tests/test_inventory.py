from datetime import date, timedelta

import pytest

from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InsufficientStockError, InvalidDataError
from restaurant.inventory.inventory import TARGET_STOCK_MULTIPLIER, Inventory


def test_total_ignores_expired_batches(inventory: Inventory, milk: Ingredient, today: date) -> None:
    inventory.receive(milk, 500, today - timedelta(days=10))
    inventory.receive(milk, 300, today)
    assert inventory.total_of(milk, today) == 300


def test_consume_uses_oldest_expiry_first(inventory: Inventory, milk: Ingredient, today: date) -> None:
    older = inventory.receive(milk, 100, today - timedelta(days=3))
    newer = inventory.receive(milk, 100, today)
    inventory.consume(milk, 150, today)
    assert older.is_empty()
    assert newer.quantity == pytest.approx(50)
    assert inventory.total_of(milk, today) == pytest.approx(50)


def test_consume_more_than_available_fails(inventory: Inventory, milk: Ingredient, today: date) -> None:
    inventory.receive(milk, 100, today)
    with pytest.raises(InsufficientStockError):
        inventory.consume(milk, 101, today)
    assert inventory.total_of(milk, today) == 100


def test_consume_rejects_non_positive_amount(inventory: Inventory, milk: Ingredient, today: date) -> None:
    with pytest.raises(InvalidDataError):
        inventory.consume(milk, 0, today)


def test_consume_all_is_atomic(inventory: Inventory, milk: Ingredient, flour: Ingredient, today: date) -> None:
    inventory.receive(milk, 100, today)
    with pytest.raises(InsufficientStockError):
        inventory.consume_all({milk: 50, flour: 10}, today)
    assert inventory.total_of(milk, today) == 100


def test_consume_all_takes_everything(inventory: Inventory, milk: Ingredient, flour: Ingredient, today: date) -> None:
    inventory.receive(milk, 100, today)
    inventory.receive(flour, 100, today)
    inventory.consume_all({milk: 40, flour: 60}, today)
    assert inventory.total_of(milk, today) == pytest.approx(60)
    assert inventory.total_of(flour, today) == pytest.approx(40)


def test_has_enough(inventory: Inventory, milk: Ingredient, today: date) -> None:
    inventory.receive(milk, 100, today)
    assert inventory.has_enough(milk, 100, today)
    assert not inventory.has_enough(milk, 100.5, today)


def test_discard_expired(inventory: Inventory, milk: Ingredient, today: date) -> None:
    old = inventory.receive(milk, 100, today - timedelta(days=10))
    inventory.receive(milk, 100, today)
    assert inventory.discard_expired(today) == [old]
    assert inventory.stock_report(today) == {milk: 100}


def test_expiring_soon(inventory: Inventory, milk: Ingredient, flour: Ingredient, today: date) -> None:
    soon = inventory.receive(milk, 100, today - timedelta(days=5))
    inventory.receive(flour, 100, today)
    inventory.receive(milk, 100, today - timedelta(days=30))
    assert inventory.expiring_soon(today, within_days=3) == [soon]


def test_shortage_amounts(inventory: Inventory, milk: Ingredient, flour: Ingredient, today: date) -> None:
    inventory.set_reorder_level(milk, 200)
    inventory.set_reorder_level(flour, 100)
    inventory.receive(milk, 50, today)
    inventory.receive(flour, 500, today)
    assert inventory.shortage_amounts(today) == {milk: 200 * TARGET_STOCK_MULTIPLIER - 50}


def test_reorder_level_cannot_be_negative(inventory: Inventory, milk: Ingredient) -> None:
    with pytest.raises(InvalidDataError):
        inventory.set_reorder_level(milk, -1)


def test_earliest_expiry_days(inventory: Inventory, milk: Ingredient, today: date) -> None:
    assert inventory.earliest_expiry_days(milk, today) is None
    inventory.receive(milk, 100, today)
    inventory.receive(milk, 100, today - timedelta(days=4))
    assert inventory.earliest_expiry_days(milk, today) == 3
