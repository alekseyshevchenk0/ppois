from __future__ import annotations

from decimal import Decimal

from restaurant.exceptions import InvalidDataError
from restaurant.money import PERCENT_BASE, percent_of
from restaurant.validation import require_non_empty, require_non_negative


class Discount:
    def __init__(self, name: str, percent: Decimal, min_order_amount: Decimal = Decimal(0)) -> None:
        require_non_empty(name, "название скидки")
        require_non_negative(min_order_amount, "минимальная сумма заказа")
        if not 0 < percent <= PERCENT_BASE:
            raise InvalidDataError(
                f"Процент скидки должен быть в диапазоне от 0 до 100, получено {percent}"
            )
        self.name = name
        self.percent = percent
        self.min_order_amount = min_order_amount

    def applies_to(self, subtotal: Decimal) -> bool:
        return subtotal >= self.min_order_amount

    def amount_off(self, subtotal: Decimal) -> Decimal:
        if not self.applies_to(subtotal):
            return Decimal(0)
        return percent_of(subtotal, self.percent)
