from __future__ import annotations

from datetime import date
from decimal import Decimal

from restaurant.exceptions import InvalidDataError
from restaurant.staff.employee import Employee
from restaurant.validation import require_positive


class Cashier(Employee):

    def __init__(
        self, name: str, phone: str, birth_date: date, hourly_rate: Decimal, hire_date: date, register_number: int
    ) -> None:
        super().__init__(name, phone, birth_date, hourly_rate, hire_date)
        require_positive(register_number, "номер кассы")
        self.register_number = register_number
        self.cash_in_till = Decimal(0)
        self.transactions_count = 0

    def accept_cash(self, amount: Decimal) -> None:
        require_positive(amount, "сумма наличных")
        self.cash_in_till += amount
        self.transactions_count += 1

    def give_change(self, amount: Decimal) -> None:
        require_positive(amount, "сумма сдачи")
        if amount > self.cash_in_till:
            raise InvalidDataError("В кассе недостаточно наличных для сдачи")
        self.cash_in_till -= amount

    def close_till(self) -> Decimal:
        collected = self.cash_in_till
        self.cash_in_till = Decimal(0)
        self.transactions_count = 0
        return collected
