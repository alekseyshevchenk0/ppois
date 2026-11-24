from decimal import Decimal

import pytest

from restaurant.exceptions import (
    AllergenConflictError,
    DishUnavailableError,
    InsufficientStockError,
    InvalidDataError,
    RestaurantError,
)
from restaurant.validation import require_non_empty, require_non_negative, require_positive


def test_all_domain_errors_share_one_base() -> None:
    errors = [InvalidDataError("x"), InsufficientStockError("a", 1, 0), DishUnavailableError("d", "r"), AllergenConflictError("d", ["a"])]
    assert all(isinstance(error, RestaurantError) for error in errors)


def test_insufficient_stock_keeps_details() -> None:
    error = InsufficientStockError("flour", 500, 120)
    assert (error.ingredient_name, error.requested, error.available) == ("flour", 500, 120)
    assert "Недостаточно ингредиента" in str(error)
    assert "flour" in str(error)


def test_allergen_conflict_lists_sorted_names() -> None:
    error = AllergenConflictError("Cake", ["milk", "eggs"])
    assert error.allergen_names == "eggs, milk"


def test_require_non_empty() -> None:
    require_non_empty("ok", "field")
    with pytest.raises(InvalidDataError, match="Поле «field» не должно быть пустым"):
        require_non_empty("   ", "field")


def test_require_positive() -> None:
    require_positive(Decimal("0.01"), "field")
    with pytest.raises(InvalidDataError):
        require_positive(0, "field")


def test_require_non_negative() -> None:
    require_non_negative(0, "field")
    with pytest.raises(InvalidDataError):
        require_non_negative(-1, "field")
