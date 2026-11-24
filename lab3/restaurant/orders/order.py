from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from restaurant.exceptions import DishUnavailableError, InvalidDataError, InvalidOrderStateError
from restaurant.guests.customer import Customer
from restaurant.hall.table import Table
from restaurant.menu.dish import Dish
from restaurant.orders.order_item import OrderItem
from restaurant.staff.waiter import Waiter
from restaurant.validation import require_positive


class OrderStatus(Enum):
    NEW = "новый"
    IN_PROGRESS = "готовится"
    READY = "готов"
    SERVED = "подан"
    PAID = "оплачен"
    CANCELLED = "отменён"


ALLOWED_TRANSITIONS = {
    OrderStatus.NEW: {OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED},
    OrderStatus.IN_PROGRESS: {OrderStatus.READY, OrderStatus.CANCELLED},
    OrderStatus.READY: {OrderStatus.SERVED},
    OrderStatus.SERVED: {OrderStatus.PAID},
    OrderStatus.PAID: set(),
    OrderStatus.CANCELLED: set(),
}


class Order:
    def __init__(self, number: int, table: Table, waiter: Waiter, guest: Customer, created_at: datetime) -> None:
        require_positive(number, "номер заказа")
        self.number = number
        self.table = table
        self.waiter = waiter
        self.guest = guest
        self.created_at = created_at
        self.status = OrderStatus.NEW
        self._items: list[OrderItem] = []

    @property
    def items(self) -> list[OrderItem]:
        return list(self._items)

    def add_item(self, dish: Dish, quantity: int = 1, note: str = "") -> OrderItem:
        self._require_new("добавить блюдо")
        if dish.is_stopped:
            raise DishUnavailableError(dish.name, "блюдо в стоп-листе")
        dish.ensure_safe_for(self.guest.profile.forbidden_allergens)
        existing = next((item for item in self._items if item.is_same_position(dish, note)), None)
        if existing is not None:
            existing.increase(quantity)
            return existing
        item = OrderItem(dish, quantity, note)
        self._items.append(item)
        return item

    def remove_item(self, dish_name: str) -> OrderItem:
        self._require_new("убрать блюдо")
        item = next((candidate for candidate in self._items if candidate.dish.name == dish_name), None)
        if item is None:
            raise InvalidDataError(f"Блюда «{dish_name}» нет в заказе №{self.number}")
        self._items.remove(item)
        return item

    def subtotal(self) -> Decimal:
        return sum((item.total() for item in self._items), Decimal(0))

    def validate_for_kitchen(self) -> None:
        self._require_new("отправить на кухню")
        if not self._items:
            raise InvalidDataError(f"Заказ №{self.number} пуст")

    def send_to_kitchen(self) -> None:
        self.validate_for_kitchen()
        self._move(OrderStatus.IN_PROGRESS, "отправить на кухню")

    def mark_ready(self) -> None:
        self._move(OrderStatus.READY, "отметить готовым")

    def mark_served(self) -> None:
        self._move(OrderStatus.SERVED, "подать гостю")

    def mark_paid(self) -> None:
        self._move(OrderStatus.PAID, "оплатить")

    def cancel(self) -> None:
        self._move(OrderStatus.CANCELLED, "отменить")

    def is_closed(self) -> bool:
        return self.status in (OrderStatus.PAID, OrderStatus.CANCELLED)

    def _require_new(self, action: str) -> None:
        if self.status is not OrderStatus.NEW:
            raise InvalidOrderStateError(self.number, self.status.value, action)

    def _move(self, new_status: OrderStatus, action: str) -> None:
        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise InvalidOrderStateError(self.number, self.status.value, action)
        self.status = new_status
