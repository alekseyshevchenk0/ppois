from __future__ import annotations

from decimal import Decimal

from restaurant.money import CENT, PERCENT_BASE, percent_of
from restaurant.staff.waiter import Waiter
from restaurant.validation import require_positive


class Tip:
    def __init__(self, waiter: Waiter, amount: Decimal) -> None:
        require_positive(amount, "tip amount")
        self.waiter = waiter
        self.amount = amount
        self.is_delivered = False

    @classmethod
    def from_percent(cls, waiter: Waiter, base_amount: Decimal, percent: Decimal) -> Tip:
        return cls(waiter, percent_of(base_amount, percent))

    def percent_of(self, base_amount: Decimal) -> Decimal:
        return (self.amount * PERCENT_BASE / base_amount).quantize(CENT)

    def deliver(self) -> None:
        if not self.is_delivered:
            self.waiter.receive_tip(self.amount)
            self.is_delivered = True
