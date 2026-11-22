from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from restaurant.staff.employee import Employee
from restaurant.validation import require_positive


class Waiter(Employee):
    role_title = "waiter"

    def __init__(
        self, name: str, phone: str, birth_date: date, hourly_rate: Decimal, hire_date: date, languages: Iterable[str] = ()
    ) -> None:
        super().__init__(name, phone, birth_date, hourly_rate, hire_date)
        self.languages = {language.lower() for language in languages}
        self.tips_total = Decimal(0)
        self.guests_served = 0

    def speaks(self, language: str) -> bool:
        return language.lower() in self.languages

    def receive_tip(self, amount: Decimal) -> None:
        require_positive(amount, "tip")
        self.tips_total += amount

    def serve_guests(self, count: int) -> None:
        require_positive(count, "guest count")
        self.ensure_active()
        self.guests_served += count

    def average_tip_per_guest(self) -> Decimal:
        if self.guests_served == 0:
            return Decimal(0)
        return self.tips_total / self.guests_served
