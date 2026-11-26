from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from typing import Iterable

from restaurant.exceptions import InvalidDataError
from restaurant.orders.payment import Payment


class SalesReport:
    def __init__(self, payments: Iterable[Payment], start_date: date, end_date: date) -> None:
        if start_date > end_date:
            raise InvalidDataError("Начальная дата не может быть позже конечной")
        self.start_date = start_date
        self.end_date = end_date
        self.payments = [
            payment for payment in payments
            if payment.is_completed and start_date <= payment.paid_at.date() <= end_date
        ]

    def orders_count(self) -> int:
        return len(self.payments)

    def total_revenue(self) -> Decimal:
        return sum((payment.bill.total_with_tip() for payment in self.payments), Decimal(0))

    def average_check(self) -> Decimal:
        if not self.payments:
            return Decimal(0)
        return (self.total_revenue() / len(self.payments)).quantize(Decimal("0.01"))

    def popular_dishes(self, limit: int | None = None) -> list[tuple[str, int]]:
        counts: Counter[str] = Counter()
        for payment in self.payments:
            for item in payment.bill.order.items:
                counts[item.dish.name] += item.quantity
        ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return ranked if limit is None else ranked[:max(0, limit)]

    def revenue_by_day(self) -> dict[date, Decimal]:
        revenue: dict[date, Decimal] = defaultdict(Decimal)
        for payment in self.payments:
            day = payment.paid_at.date()
            revenue[day] += payment.bill.total_with_tip()
        return dict(sorted(revenue.items()))
