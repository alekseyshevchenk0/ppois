from __future__ import annotations

from datetime import date
from decimal import Decimal

from restaurant.exceptions import InvalidDataError
from restaurant.money import percent_of
from restaurant.orders.discount import Discount
from restaurant.orders.order import Order
from restaurant.orders.promo_code import PromoCode
from restaurant.orders.tip import Tip

MAX_TOTAL_DISCOUNT_PERCENT = Decimal(30)


class Bill:
    def __init__(self, order: Order) -> None:
        self.order = order
        self.tip: Tip | None = None
        self.is_settled = False
        self._discounts: list[Discount] = []

    @property
    def discounts(self) -> list[Discount]:
        return list(self._discounts)

    def apply_discount(self, discount: Discount) -> None:
        self._ensure_can_apply(discount)
        self._discounts.append(discount)

    def apply_promo(self, promo: PromoCode, day: date) -> None:
        self._ensure_can_apply(promo.discount)
        self._discounts.append(promo.redeem(day))

    def discount_percent_total(self) -> Decimal:
        requested = sum((discount.percent for discount in self._discounts), Decimal(0))
        return min(requested, MAX_TOTAL_DISCOUNT_PERCENT)

    def discount_amount(self) -> Decimal:
        return percent_of(self.order.subtotal(), self.discount_percent_total())

    def total_due(self) -> Decimal:
        return self.order.subtotal() - self.discount_amount()

    def add_tip(self, tip: Tip) -> None:
        self.tip = tip

    def total_with_tip(self) -> Decimal:
        return self.total_due() + (self.tip.amount if self.tip else Decimal(0))

    def settle(self) -> None:
        self.order.mark_paid()
        if self.tip is not None:
            self.tip.deliver()
        self.is_settled = True

    def receipt_lines(self) -> list[str]:
        lines = [f"{item.dish.name} × {item.quantity} = {item.total()}" for item in self.order.items]
        lines.append(f"Сумма заказа: {self.order.subtotal()}")
        if self._discounts:
            lines.append(f"Скидка {self.discount_percent_total()}%: -{self.discount_amount()}")
        if self.tip is not None:
            lines.append(f"Чаевые: {self.tip.amount}")
        lines.append(f"К оплате: {self.total_with_tip()}")
        return lines

    def _ensure_can_apply(self, discount: Discount) -> None:
        if any(known.name == discount.name for known in self._discounts):
            raise InvalidDataError(f"Скидка «{discount.name}» уже применена")
        if not discount.applies_to(self.order.subtotal()):
            raise InvalidDataError(f"Скидка «{discount.name}» действует от суммы {discount.min_order_amount}")
