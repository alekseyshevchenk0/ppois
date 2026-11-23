from __future__ import annotations

from datetime import date
from decimal import Decimal

from restaurant.exceptions import EmployeeNotAvailableError
from restaurant.staff.employee import Employee


class Courier(Employee):
    role_title = "курьер"

    def __init__(
        self,
        name: str,
        phone: str,
        birth_date: date,
        hourly_rate: Decimal,
        hire_date: date,
        transport: str,
    ) -> None:
        super().__init__(name, phone, birth_date, hourly_rate, hire_date)
        self.transport = transport
        self.active_delivery_number: int | None = None
        self.completed_deliveries = 0

    def assign_delivery(self, delivery_number: int) -> None:
        self.ensure_active()
        if self.active_delivery_number is not None:
            raise EmployeeNotAvailableError(self.name, "уже выполняется доставка")
        self.active_delivery_number = delivery_number

    def complete_delivery(self, delivery_number: int) -> None:
        if self.active_delivery_number != delivery_number:
            raise EmployeeNotAvailableError(self.name, "эта доставка не закреплена за курьером")
        self.active_delivery_number = None
        self.completed_deliveries += 1

    def is_available(self) -> bool:
        return self.is_active and self.active_delivery_number is None
