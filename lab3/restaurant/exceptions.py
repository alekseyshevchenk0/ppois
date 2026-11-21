from __future__ import annotations

from collections.abc import Iterable


class RestaurantError(Exception):
    """Base class for every error raised by the restaurant domain."""


class InvalidDataError(RestaurantError):
    """Raised when an object is created or changed with invalid data."""


class InsufficientStockError(RestaurantError):
    """Raised when the inventory holds less of an ingredient than requested."""

    def __init__(self, ingredient_name: str, requested: float, available: float) -> None:
        super().__init__(f"Not enough '{ingredient_name}': requested {requested}, available {available}")
        self.ingredient_name = ingredient_name
        self.requested = requested
        self.available = available


class DishUnavailableError(RestaurantError):
    """Raised when a dish cannot be cooked right now."""

    def __init__(self, dish_name: str, reason: str) -> None:
        super().__init__(f"Dish '{dish_name}' is unavailable: {reason}")
        self.dish_name = dish_name
        self.reason = reason


class AllergenConflictError(RestaurantError):
    """Raised when a dish contains an allergen the guest must avoid."""

    def __init__(self, dish_name: str, allergen_names: Iterable[str]) -> None:
        names = ", ".join(sorted(allergen_names))
        super().__init__(f"Dish '{dish_name}' contains forbidden allergens: {names}")
        self.dish_name = dish_name
        self.allergen_names = names