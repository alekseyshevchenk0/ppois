from decimal import Decimal

import pytest

from restaurant.catalog.allergen import Allergen
from restaurant.exceptions import AllergenConflictError, DishUnavailableError, InvalidDataError, InvalidOrderStateError
from restaurant.menu.dish import Dish
from restaurant.orders.order import Order, OrderStatus
from restaurant.orders.order_item import OrderItem
from tests.constants import NOW


def test_item_total_and_quantity(pancakes: Dish) -> None:
    item = OrderItem(pancakes, 2)
    assert item.total() == Decimal("15.00")
    item.change_quantity(3)
    assert item.total() == Decimal("22.50")
    item.increase(1)
    assert item.quantity == 4
    with pytest.raises(InvalidDataError):
        item.change_quantity(0)
    with pytest.raises(InvalidDataError):
        item.increase(0)
    with pytest.raises(InvalidDataError):
        OrderItem(pancakes, 0)


def test_item_keeps_the_price_from_the_moment_of_order(pancakes: Dish) -> None:
    item = OrderItem(pancakes, 1)
    pancakes.change_price_by_percent(Decimal(100))
    assert item.unit_price == Decimal("7.50")


def test_item_cooking_minutes(pancakes: Dish) -> None:
    assert OrderItem(pancakes, 2).cooking_minutes() == 10
    assert OrderItem(pancakes, 3).cooking_minutes() == 20


def test_order_number_validation(medium_table, waiter, adult_guest) -> None:
    with pytest.raises(InvalidDataError):
        Order(0, medium_table, waiter, adult_guest, NOW)


def test_same_dish_with_same_note_is_merged(order: Order, pancakes: Dish) -> None:
    first = order.add_item(pancakes, 1)
    second = order.add_item(pancakes, 2)
    assert first is second
    assert len(order.items) == 1
    assert order.items[0].quantity == 3


def test_different_note_makes_a_separate_position(order: Order, pancakes: Dish) -> None:
    order.add_item(pancakes, 1)
    order.add_item(pancakes, 1, note="без молока")
    assert len(order.items) == 2


def test_stopped_dish_cannot_be_ordered(order: Order, pancakes: Dish) -> None:
    pancakes.stop()
    with pytest.raises(DishUnavailableError):
        order.add_item(pancakes)


def test_allergen_of_the_guest_is_checked(order: Order, pancakes: Dish) -> None:
    order.guest.profile.add_allergen(Allergen.MILK)
    with pytest.raises(AllergenConflictError):
        order.add_item(pancakes)
    assert order.items == []


def test_remove_item_and_subtotal(order: Order, pancakes: Dish, salad: Dish) -> None:
    order.add_item(pancakes, 2)
    order.add_item(salad, 1)
    assert order.subtotal() == Decimal("20.00")
    assert order.remove_item("Tomato salad").dish is salad
    assert order.subtotal() == Decimal("15.00")
    with pytest.raises(InvalidDataError):
        order.remove_item("Tomato salad")


def test_status_flow(order: Order, pancakes: Dish) -> None:
    order.add_item(pancakes)
    order.send_to_kitchen()
    assert order.status is OrderStatus.IN_PROGRESS
    order.mark_ready()
    order.mark_served()
    assert not order.is_closed()
    order.mark_paid()
    assert order.status is OrderStatus.PAID
    assert order.is_closed()


def test_order_cannot_skip_statuses(order: Order, pancakes: Dish) -> None:
    order.add_item(pancakes)
    with pytest.raises(InvalidOrderStateError):
        order.mark_ready()
    order.send_to_kitchen()
    with pytest.raises(InvalidOrderStateError):
        order.mark_paid()


def test_order_cannot_be_changed_after_sending(order: Order, pancakes: Dish, salad: Dish) -> None:
    order.add_item(pancakes)
    order.send_to_kitchen()
    with pytest.raises(InvalidOrderStateError):
        order.add_item(salad)
    with pytest.raises(InvalidOrderStateError):
        order.remove_item("Pancakes")
    with pytest.raises(InvalidOrderStateError):
        order.send_to_kitchen()


def test_empty_order_cannot_be_sent(order: Order) -> None:
    with pytest.raises(InvalidDataError):
        order.send_to_kitchen()


def test_cancel(order: Order, pancakes: Dish) -> None:
    order.add_item(pancakes)
    order.cancel()
    assert order.is_closed()
    with pytest.raises(InvalidOrderStateError):
        order.send_to_kitchen()


def test_served_order_cannot_be_cancelled(order: Order, pancakes: Dish) -> None:
    order.add_item(pancakes)
    order.send_to_kitchen()
    order.mark_ready()
    order.mark_served()
    with pytest.raises(InvalidOrderStateError):
        order.cancel()
