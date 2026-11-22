from __future__ import annotations

from datetime import date
from decimal import Decimal

from restaurant.exceptions import EmployeeNotAvailableError
from restaurant.money import apply_percent
from restaurant.person import Person
from restaurant.validation import require_positive

DAYS_IN_YEAR = 365


class Employee(Person):
    role_title = "employee"

    def __init__(self, name: str, phone: str, birth_date: date, hourly_rate: Decimal, hire_date: date) -> None:
        super().__init__(name, phone, birth_date)
        require_positive(hourly_rate, "hourly rate")
        self.hourly_rate = hourly_rate
        self.hire_date = hire_date
        self.is_active = True

    def years_of_service(self, today: date) -> int:
        return (today - self.hire_date).days // DAYS_IN_YEAR

    def give_raise(self, percent: Decimal) -> Decimal:
        require_positive(percent, "raise percent")
        self.hourly_rate = apply_percent(self.hourly_rate, percent)
        return self.hourly_rate

    def dismiss(self) -> None:
        self.is_active = False

    def reinstate(self) -> None:
        self.is_active = True

    def ensure_active(self) -> None:
        if not self.is_active:
            raise EmployeeNotAvailableError(self.name, "the employee has been dismissed")
