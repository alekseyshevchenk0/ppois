from __future__ import annotations

from datetime import date
from decimal import Decimal

from restaurant.exceptions import EmployeeNotAvailableError, UnderageGuestError
from restaurant.guests.customer import Customer
from restaurant.staff.employee import Employee


class Bartender(Employee):

    def __init__(
        self, name: str, phone: str, birth_date: date, hourly_rate: Decimal, hire_date: date, is_alcohol_certified: bool = True
    ) -> None:
        super().__init__(name, phone, birth_date, hourly_rate, hire_date)
        self.is_alcohol_certified = is_alcohol_certified
        self.drinks_made = 0

    def can_serve_alcohol_to(self, guest: Customer, today: date) -> bool:
        return self.is_active and self.is_alcohol_certified and guest.is_adult(today)

    def serve_drink(self, guest: Customer, today: date, alcoholic: bool = False) -> None:
        self.ensure_active()
        if alcoholic:
            self._check_alcohol_rules(guest, today)
        self.drinks_made += 1

    def _check_alcohol_rules(self, guest: Customer, today: date) -> None:
        if not self.is_alcohol_certified:
            raise EmployeeNotAvailableError(self.name, "нет сертификата на продажу алкоголя")
        if not guest.is_adult(today):
            raise UnderageGuestError(guest.name, guest.age_on(today))
