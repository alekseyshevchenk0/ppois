from datetime import date
from decimal import Decimal

import pytest

from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InvalidDataError
from restaurant.inventory.supplier import Supplier


def test_supplier_validation() -> None:
    with pytest.raises(InvalidDataError):
        Supplier("", "123", 1)
    with pytest.raises(InvalidDataError):
        Supplier("Farm", "", 1)
    with pytest.raises(InvalidDataError):
        Supplier("Farm", "123", -1)


def test_supplier_prices(supplier: Supplier, flour: Ingredient, tomato: Ingredient) -> None:
    assert supplier.supplies(flour)
    assert not supplier.supplies(tomato)
    assert supplier.price_of(flour) == Decimal("0.002")
    with pytest.raises(InvalidDataError):
        supplier.price_of(tomato)


def test_set_price_must_be_positive(supplier: Supplier, flour: Ingredient) -> None:
    with pytest.raises(InvalidDataError):
        supplier.set_price(flour, Decimal(0))


def test_quote_and_delivery(supplier: Supplier, flour: Ingredient) -> None:
    assert supplier.quote(flour, 1000) == Decimal("2.000")
    assert supplier.delivery_date(date(2026, 11, 21)) == date(2026, 11, 23)
    with pytest.raises(InvalidDataError):
        supplier.quote(flour, 0)
