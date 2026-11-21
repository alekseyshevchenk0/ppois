"""Small validation helpers shared by all domain classes."""
from __future__ import annotations

from decimal import Decimal

from restaurant.exceptions import InvalidDataError


def require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise InvalidDataError(f"{field_name} must not be empty")


def require_positive(value: float | Decimal, field_name: str) -> None:
    if value <= 0:
        raise InvalidDataError(f"{field_name} must be positive, got {value}")


def require_non_negative(value: float | Decimal, field_name: str) -> None:
    if value < 0:
        raise InvalidDataError(f"{field_name} must not be negative, got {value}")
