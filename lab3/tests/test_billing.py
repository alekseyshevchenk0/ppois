from datetime import date
from decimal import Decimal

import pytest

from restaurant.exceptions import InvalidDataError, InvalidOrderStateError, InvalidPromoCodeError
from restaurant.guests.loyalty import LoyaltyCard
from restaurant.menu.dish import Dish
from restaurant.orders.bill import LOYALTY_DISCOUNT_NAME, Bill
from restaurant.orders.discount import Discount
from restaurant.orders.order import Order
from restaurant.orders.promo_code import PromoCode
from restaurant.orders.tip import Tip
from restaurant.staff.waiter import Waiter
from tests.constants import TODAY


@pytest.fixture
def bill(order: Order, pancakes: Dish) -> Bill:
    order.add_item(pancakes, 2)
    return Bill(order)


def make_promo(percent: int = 15, min_amount: int = 0, max_uses: int = 1) -> PromoCode:
    discount = Discount("Зима", Decimal(percent), Decimal(min_amount))
    return PromoCode("WINTER", discount, date(2026, 11, 1), date(2026, 12, 31), max_uses)


def test_discount_validation() -> None:
    with pytest.raises(InvalidDataError):
        Discount("Скидка", Decimal(0))
    with pytest.raises(InvalidDataError):
        Discount("Скидка", Decimal(101))
    with pytest.raises(InvalidDataError):
        Discount("Скидка", Decimal(10), Decimal(-1))
    with pytest.raises(InvalidDataError):
        Discount(" ", Decimal(10))


def test_discount_amount() -> None:
    discount = Discount("Скидка", Decimal(10), Decimal(50))
    assert discount.applies_to(Decimal(50))
    assert discount.amount_off(Decimal(200)) == Decimal("20.00")
    assert discount.amount_off(Decimal(49)) == Decimal(0)


def test_promo_validation() -> None:
    discount = Discount("Зима", Decimal(10))
    with pytest.raises(InvalidDataError):
        PromoCode("X", discount, date(2026, 12, 1), date(2026, 11, 1), 1)
    with pytest.raises(InvalidDataError):
        PromoCode("X", discount, date(2026, 11, 1), date(2026, 12, 1), 0)


def test_promo_redeem_and_limits() -> None:
    promo = make_promo(max_uses=2)
    assert promo.remaining_uses() == 2
    promo.redeem(TODAY)
    promo.redeem(TODAY)
    with pytest.raises(InvalidPromoCodeError, match="лимит"):
        promo.redeem(TODAY)


def test_promo_dates() -> None:
    promo = make_promo()
    assert not promo.is_valid_on(date(2026, 10, 31))
    assert promo.is_valid_on(date(2026, 12, 31))
    with pytest.raises(InvalidPromoCodeError, match="срок"):
        promo.redeem(date(2027, 1, 1))


def test_tip(waiter: Waiter) -> None:
    tip = Tip.from_percent(waiter, Decimal(100), Decimal(10))
    assert tip.amount == Decimal("10.00")
    assert tip.percent_of(Decimal(50)) == Decimal("20.00")
    tip.deliver()
    tip.deliver()
    assert waiter.tips_total == Decimal("10.00")
    with pytest.raises(InvalidDataError):
        Tip(waiter, Decimal(0))


def test_bill_without_discounts(bill: Bill) -> None:
    assert bill.total_due() == Decimal("15.00")
    assert bill.discount_amount() == Decimal("0.00")


def test_discount_reduces_the_total(bill: Bill) -> None:
    bill.apply_discount(Discount("Скидка дня", Decimal(10)))
    assert bill.discount_amount() == Decimal("1.50")
    assert bill.total_due() == Decimal("13.50")


def test_discount_cannot_be_applied_twice_or_below_minimum(bill: Bill) -> None:
    bill.apply_discount(Discount("Скидка дня", Decimal(10)))
    with pytest.raises(InvalidDataError, match="уже применена"):
        bill.apply_discount(Discount("Скидка дня", Decimal(5)))
    with pytest.raises(InvalidDataError, match="действует от суммы"):
        bill.apply_discount(Discount("Крупная", Decimal(5), Decimal(100)))


def test_promo_is_redeemed_once_per_bill(bill: Bill) -> None:
    promo = make_promo()
    bill.apply_promo(promo, TODAY)
    assert promo.remaining_uses() == 0
    assert bill.total_due() == Decimal("12.75")


def test_unusable_promo_is_not_spent(bill: Bill) -> None:
    promo = make_promo(min_amount=100)
    with pytest.raises(InvalidDataError):
        bill.apply_promo(promo, TODAY)
    assert promo.remaining_uses() == 1


def test_loyalty_discount_follows_the_card(bill: Bill, today: date) -> None:
    bill.apply_loyalty()
    assert bill.discounts == []
    card = LoyaltyCard("S-1", today)
    card.earn_points(Decimal(5000))
    bill.order.guest.attach_card(card)
    bill.apply_loyalty()
    assert bill.discounts[0].name == LOYALTY_DISCOUNT_NAME
    assert bill.discount_percent_total() == Decimal(5)


def test_total_discount_is_capped(bill: Bill, today: date) -> None:
    card = LoyaltyCard("S-1", today)
    card.earn_points(Decimal(5000))
    bill.order.guest.attach_card(card)
    bill.apply_loyalty()
    bill.apply_promo(make_promo(percent=25), TODAY)
    bill.apply_discount(Discount("Скидка дня", Decimal(10)))
    assert bill.discount_percent_total() == Decimal(30)
    assert bill.total_due() == Decimal("10.50")


def test_tip_and_receipt(bill: Bill, waiter: Waiter) -> None:
    bill.add_tip(Tip(waiter, Decimal(3)))
    bill.apply_discount(Discount("Скидка дня", Decimal(10)))
    lines = bill.receipt_lines()
    assert lines[0] == "Pancakes × 2 = 15.00"
    assert lines[-1] == "К оплате: 16.50"
    assert any(line.startswith("Скидка 10%") for line in lines)
    assert "Чаевые: 3" in lines


def test_receipt_without_extras(bill: Bill) -> None:
    assert bill.receipt_lines() == ["Pancakes × 2 = 15.00", "Сумма заказа: 15.00", "К оплате: 15.00"]


def test_settle_requires_served_order(bill: Bill) -> None:
    with pytest.raises(InvalidOrderStateError):
        bill.settle()
    assert not bill.is_settled


def test_settle_pays_the_order_and_delivers_the_tip(bill: Bill, waiter: Waiter) -> None:
    bill.add_tip(Tip(waiter, Decimal(3)))
    bill.order.send_to_kitchen()
    bill.order.mark_ready()
    bill.order.mark_served()
    bill.settle()
    assert bill.is_settled
    assert bill.order.is_closed()
    assert waiter.tips_total == Decimal(3)
