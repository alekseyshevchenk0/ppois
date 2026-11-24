from __future__ import annotations

from decimal import Decimal

from restaurant.exceptions import InvalidDataError


def require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise InvalidDataError(f"Поле «{field_name}» не должно быть пустым")


def require_positive(value: float | Decimal, field_name: str) -> None:
    if value <= 0:
        raise InvalidDataError(f"Поле «{field_name}» должно быть положительным, получено: {value}")


def require_non_negative(value: float | Decimal, field_name: str) -> None:
    if value < 0:
        raise InvalidDataError(f"Поле «{field_name}» не должно быть отрицательным, получено: {value}")
