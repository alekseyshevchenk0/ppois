from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime


class RestaurantError(Exception):
    pass


class InvalidDataError(RestaurantError):
    pass


class InsufficientStockError(RestaurantError):
    def __init__(self, ingredient_name: str, requested: float, available: float) -> None:
        super().__init__(
            f"Недостаточно ингредиента «{ingredient_name}»: "
            f"требуется {requested}, доступно {available}"
        )
        self.ingredient_name = ingredient_name
        self.requested = requested
        self.available = available


class DishUnavailableError(RestaurantError):
    def __init__(self, dish_name: str, reason: str) -> None:
        super().__init__(f"Блюдо «{dish_name}» недоступно: {reason}")
        self.dish_name = dish_name
        self.reason = reason


class AllergenConflictError(RestaurantError):
    def __init__(self, dish_name: str, allergen_names: Iterable[str]) -> None:
        names = ", ".join(sorted(allergen_names))
        super().__init__(f"Блюдо «{dish_name}» содержит аллергены, которых следует избегать: {names}")
        self.dish_name = dish_name
        self.allergen_names = names


class EmployeeNotAvailableError(RestaurantError):
    def __init__(self, employee_name: str, reason: str) -> None:
        super().__init__(f"Сотрудник «{employee_name}» недоступен: {reason}")
        self.employee_name = employee_name
        self.reason = reason


class UnderageGuestError(RestaurantError):
    def __init__(self, guest_name: str, age: int) -> None:
        super().__init__(f"Гостю «{guest_name}» {age} лет, ему нельзя подавать алкоголь")
        self.guest_name = guest_name
        self.age = age


class TableUnavailableError(RestaurantError):
    def __init__(self, subject: str, reason: str) -> None:
        super().__init__(f"{subject} недоступен: {reason}")
        self.subject = subject
        self.reason = reason


class ReservationConflictError(RestaurantError):
    def __init__(self, table_number: int, start: datetime) -> None:
        super().__init__(f"Стол №{table_number} уже занят на {start:%d.%m.%Y %H:%M}")
        self.table_number = table_number
        self.start = start


class OrderNotFoundError(RestaurantError):
    def __init__(self, order_number: int) -> None:
        super().__init__(f"Заказ №{order_number} не найден")
        self.order_number = order_number


class InvalidOrderStateError(RestaurantError):
    def __init__(self, order_number: int, status: str, action: str) -> None:
        super().__init__(
            f"Заказ №{order_number}: нельзя выполнить действие «{action}» "
            f"в статусе «{status}»"
        )
        self.order_number = order_number
        self.status = status
        self.action = action


class PaymentDeclinedError(RestaurantError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Платёж отклонён: {reason}")
        self.reason = reason


class InvalidPromoCodeError(RestaurantError):
    def __init__(self, code: str, reason: str) -> None:
        super().__init__(f"Промокод «{code}» недействителен: {reason}")
        self.code = code
        self.reason = reason


class KitchenOverloadError(RestaurantError):
    def __init__(self, station_name: str, reason: str) -> None:
        super().__init__(f"Станция «{station_name}» перегружена: {reason}")
        self.station_name = station_name
        self.reason = reason
