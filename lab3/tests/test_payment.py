from decimal import Decimal

import pytest

from restaurant.exceptions import InvalidOrderStateError, PaymentDeclinedError
from restaurant.menu.dish import Dish
from restaurant.orders.bill import Bill
from restaurant.orders.order import Order, OrderStatus
from restaurant.orders.payment import Payment, PaymentMethod
from restaurant.orders.tip import Tip
from restaurant.staff.cashier import Cashier
from restaurant.staff.waiter import Waiter
from tests.constants import NOW


@pytest.fixture
def bill(order: Order, pancakes: Dish) -> Bill:
    order.add_item(pancakes, 2)
    order.send_to_kitchen()
    order.mark_ready()
    order.mark_served()
    return Bill(order)


def test_cash_payment_with_change(bill: Bill, cashier: Cashier) -> None:
    payment = Payment(bill, PaymentMethod.CASH, Decimal(20), NOW)
    payment.process(cashier)
    assert payment.is_completed
    assert payment.change == Decimal("5.00")
    assert cashier.cash_in_till == Decimal("15.00")
    assert bill.order.status is OrderStatus.PAID


def test_cash_payment_without_change(bill: Bill, cashier: Cashier) -> None:
    payment = Payment(bill, PaymentMethod.CASH, Decimal("15.00"), NOW)
    payment.process(cashier)
    assert payment.change == Decimal(0)
    assert cashier.cash_in_till == Decimal("15.00")


def test_cash_payment_declined_when_not_enough_money(bill: Bill, cashier: Cashier) -> None:
    with pytest.raises(PaymentDeclinedError, match="внесено"):
        Payment(bill, PaymentMethod.CASH, Decimal(10), NOW).process(cashier)
    assert bill.order.status is OrderStatus.SERVED


def test_cash_payment_needs_a_cashier(bill: Bill) -> None:
    with pytest.raises(PaymentDeclinedError, match="кассир"):
        Payment(bill, PaymentMethod.CASH, Decimal(20), NOW).process()


def test_card_payment_takes_the_exact_amount(bill: Bill) -> None:
    with pytest.raises(PaymentDeclinedError):
        Payment(bill, PaymentMethod.CARD, Decimal(20), NOW).process()
    Payment(bill, PaymentMethod.CARD, Decimal("15.00"), NOW).process()
    assert bill.is_settled


def test_card_payment_includes_the_tip(bill: Bill, waiter: Waiter) -> None:
    bill.add_tip(Tip(waiter, Decimal(3)))
    Payment(bill, PaymentMethod.CARD, Decimal("18.00"), NOW).process()
    assert waiter.tips_total == Decimal(3)


def test_payment_cannot_be_processed_twice(bill: Bill, cashier: Cashier) -> None:
    payment = Payment(bill, PaymentMethod.CASH, Decimal(15), NOW)
    payment.process(cashier)
    with pytest.raises(InvalidOrderStateError):
        payment.process(cashier)
