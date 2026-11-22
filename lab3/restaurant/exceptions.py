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

class EmployeeNotAvailableError(RestaurantError):
    """Raised when an employee cannot take a shift or a task."""

    def __init__(self, employee_name: str, reason: str) -> None:
        super().__init__(f"Employee '{employee_name}' is not available: {reason}")
        self.employee_name = employee_name
        self.reason = reason

class InsufficientPointsError(RestaurantError):
    """Raised when a loyalty card has fewer points than the guest wants to spend."""

    def __init__(self, requested: int, available: int) -> None:
        super().__init__(f"Not enough loyalty points: requested {requested}, available {available}")
        self.requested = requested
        self.available = available

class UnderageGuestError(RestaurantError):
    """Raised when alcohol is requested by a guest who is not an adult."""

    def __init__(self, guest_name: str, age: int) -> None:
        super().__init__(f"Guest '{guest_name}' is {age} years old and cannot be served alcohol")
        self.guest_name = guest_name
        self.age = age