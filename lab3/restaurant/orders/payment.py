from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from restaurant.exceptions import InvalidOrderStateError, PaymentDeclinedError
from restaurant.orders.bill import Bill
from restaurant.staff.cashier import Cashier


class PaymentMethod(Enum):
    CASH = "наличные"
    CARD = "карта"


class Payment:
    def __init__(self, bill: Bill, method: PaymentMethod, tendered: Decimal, paid_at: datetime) -> None:
        self.bill = bill
        self.method = method
        self.tendered = tendered
        self.paid_at = paid_at
        self.change = Decimal(0)
        self.is_completed = False

    def process(self, cashier: Cashier | None = None) -> None:
        if self.is_completed:
            raise InvalidOrderStateError(self.bill.order.number, self.bill.order.status.value, "оплатить повторно")
        due = self.bill.total_with_tip()
        handlers = {PaymentMethod.CASH: self._pay_cash, PaymentMethod.CARD: self._pay_card}
        handlers[self.method](due, cashier)
        self.bill.settle()
        self.is_completed = True

    def _pay_cash(self, due: Decimal, cashier: Cashier | None) -> None:
        if cashier is None:
            raise PaymentDeclinedError("для оплаты наличными нужен кассир")
        if self.tendered < due:
            raise PaymentDeclinedError(f"внесено {self.tendered}, к оплате {due}")
        cashier.accept_cash(self.tendered)
        self.change = self.tendered - due
        if self.change > 0:
            cashier.give_change(self.change)

    def _pay_card(self, due: Decimal, cashier: Cashier | None) -> None:
        if self.tendered != due:
            raise PaymentDeclinedError(f"с карты списывается ровно {due}, указано {self.tendered}")
