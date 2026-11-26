from datetime import date, timedelta
from decimal import Decimal

import pytest

from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InvalidDataError
from restaurant.inventory.inventory import Inventory
from restaurant.inventory.purchase_order import PurchaseOrder
from restaurant.inventory.supplier import Supplier


def test_add_line_accumulates(supplier: Supplier, flour: Ingredient, today: date) -> None:
    order = PurchaseOrder(supplier, today)
    order.add_line(flour, 100)
    order.add_line(flour, 50)
    assert order.lines == {flour: 150}


def test_add_line_validation(supplier: Supplier, flour: Ingredient, tomato: Ingredient, today: date) -> None:
    order = PurchaseOrder(supplier, today)
    with pytest.raises(InvalidDataError):
        order.add_line(tomato, 10)
    with pytest.raises(InvalidDataError):
        order.add_line(flour, 0)


def test_total_cost_and_delivery(supplier: Supplier, flour: Ingredient, milk: Ingredient, today: date) -> None:
    order = PurchaseOrder(supplier, today)
    order.add_line(flour, 1000)
    order.add_line(milk, 2000)
    assert order.total_cost() == Decimal("4.000")
    assert order.expected_delivery() == today + timedelta(days=2)


def test_receive_into_inventory_only_once(supplier: Supplier, flour: Ingredient, today: date) -> None:
    inventory = Inventory()
    order = PurchaseOrder(supplier, today)
    order.add_line(flour, 700)
    order.receive_into(inventory, today)
    assert order.is_received
    assert inventory.total_of(flour, today) == 700
    with pytest.raises(InvalidDataError):
        order.receive_into(inventory, today)


def test_order_for_shortages_skips_unsupplied(
    supplier: Supplier, flour: Ingredient, tomato: Ingredient, inventory: Inventory, today: date
) -> None:
    inventory.set_reorder_level(flour, 100)
    inventory.set_reorder_level(tomato, 100)
    order = PurchaseOrder.for_shortages(supplier, inventory, today)
    assert list(order.lines) == [flour]
