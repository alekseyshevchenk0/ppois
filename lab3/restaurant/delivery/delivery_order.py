from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from restaurant.delivery.courier import Courier
from restaurant.exceptions import InvalidDataError
from restaurant.guests.customer import Customer
from restaurant.menu.dish import Dish
from restaurant.orders.order_item import OrderItem
from restaurant.validation import require_non_empty, require_positive


class DeliveryStatus(Enum):
    NEW = "новый"
    ASSIGNED = "назначен курьер"
    PICKED_UP = "в пути"
    DELIVERED = "доставлен"
    CANCELLED = "отменён"


class DeliveryOrder:
    def __init__(
        self,
        number: int,
        customer: Customer,
        address: str,
        created_at: datetime,
        delivery_fee: Decimal = Decimal(0),
    ) -> None:
        require_positive(number, "номер доставки")
        require_non_empty(address, "адрес доставки")
        if delivery_fee < 0:
            raise InvalidDataError("Стоимость доставки не может быть отрицательной")
        self.number = number
        self.customer = customer
        self.address = address
        self.created_at = created_at
        self.delivery_fee = delivery_fee
        self.status = DeliveryStatus.NEW
        self.courier: Courier | None = None
        self._items: list[OrderItem] = []

    @property
    def items(self) -> list[OrderItem]:
        return list(self._items)

    def add_item(self, dish: Dish, quantity: int = 1, note: str = "") -> OrderItem:
        self._ensure_new()
        if dish.is_stopped or not self.customer.can_eat(dish):
            raise InvalidDataError(f"Блюдо «{dish.name}» нельзя добавить в доставку")
        item = OrderItem(dish, quantity, note)
        self._items.append(item)
        return item

    def assign_courier(self, courier: Courier) -> None:
        self._ensure_status(DeliveryStatus.NEW)
        if not self._items:
            raise InvalidDataError("Нельзя назначить курьера для пустого заказа")
        courier.assign_delivery(self.number)
        self.courier = courier
        self.status = DeliveryStatus.ASSIGNED

    def pick_up(self) -> None:
        self._ensure_status(DeliveryStatus.ASSIGNED)
        self.status = DeliveryStatus.PICKED_UP

    def deliver(self) -> None:
        self._ensure_status(DeliveryStatus.PICKED_UP)
        if self.courier is None:
            raise InvalidDataError("У доставки не назначен курьер")
        self.courier.complete_delivery(self.number)
        self.status = DeliveryStatus.DELIVERED

    def cancel(self) -> None:
        if self.status in (DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED):
            raise InvalidDataError("Завершённую доставку нельзя отменить")
        if self.courier is not None and self.courier.active_delivery_number == self.number:
            self.courier.complete_delivery(self.number)
        self.status = DeliveryStatus.CANCELLED

    def subtotal(self) -> Decimal:
        return sum((item.total() for item in self._items), Decimal(0))

    def total(self) -> Decimal:
        return self.subtotal() + self.delivery_fee

    def _ensure_new(self) -> None:
        self._ensure_status(DeliveryStatus.NEW)

    def _ensure_status(self, expected: DeliveryStatus) -> None:
        if self.status is not expected:
            raise InvalidDataError(f"Действие недоступно при статусе «{self.status.value}»")
