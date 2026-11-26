from datetime import timedelta

import pytest

from restaurant.exceptions import (
    DishUnavailableError,
    EmployeeNotAvailableError,
    InvalidDataError,
    KitchenOverloadError,
    OrderNotFoundError,
)
from restaurant.inventory.inventory import Inventory
from restaurant.kitchen.kitchen import Kitchen
from restaurant.kitchen.kitchen_station import KitchenStation
from restaurant.menu.dish import Dish
from restaurant.orders.order import Order, OrderStatus
from restaurant.staff.cook import Cook
from tests.constants import ADULT_BIRTH, COLD_STATION, HIRED_ON, HOT_STATION, HOURLY_RATE, NOW, PHONE


def full_order(order: Order, pancakes: Dish, salad: Dish) -> Order:
    order.add_item(pancakes, 2)
    order.add_item(salad, 1)
    return order


def test_station_validation() -> None:
    with pytest.raises(InvalidDataError):
        KitchenStation(" ", 30)
    with pytest.raises(InvalidDataError):
        KitchenStation(HOT_STATION, 0)


def test_station_accepts_only_its_own_cooks(hot_station: KitchenStation, hot_cook: Cook, cold_cook: Cook) -> None:
    with pytest.raises(EmployeeNotAvailableError):
        hot_station.add_cook(cold_cook)
    with pytest.raises(InvalidDataError):
        hot_station.add_cook(hot_cook)
    dismissed = Cook("Petr", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, station=HOT_STATION)
    dismissed.dismiss()
    with pytest.raises(EmployeeNotAvailableError):
        hot_station.add_cook(dismissed)
    assert hot_station.cooks_count() == 1


def test_station_without_cooks_is_overloaded() -> None:
    station = KitchenStation(HOT_STATION, 30)
    with pytest.raises(KitchenOverloadError, match="нет поваров"):
        station.speed_factor()
    with pytest.raises(KitchenOverloadError):
        station.estimate_ready_minutes(10)


def test_experienced_cook_speeds_up_the_station(hot_station: KitchenStation, hot_cook: Cook) -> None:
    assert hot_station.effective_minutes(10) == 10
    hot_cook.promote()
    hot_cook.promote()
    assert hot_station.effective_minutes(10) == 8


def test_second_cook_halves_the_queue(
    kitchen: Kitchen, hot_station: KitchenStation, order: Order, pancakes: Dish
) -> None:
    order.add_item(pancakes, 2)
    kitchen.accept_order(order, NOW)
    assert hot_station.estimate_ready_minutes(10) == 20
    hot_station.add_cook(Cook("Oleg", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, station=HOT_STATION))
    assert hot_station.estimate_ready_minutes(10) == 15


def test_kitchen_rejects_duplicate_and_unknown_stations(kitchen: Kitchen, hot_station: KitchenStation, pancakes: Dish) -> None:
    with pytest.raises(InvalidDataError):
        kitchen.add_station(hot_station)
    with pytest.raises(InvalidDataError, match="нет станции"):
        Kitchen(Inventory()).station_for(pancakes)


def test_order_estimate_is_the_slowest_station(kitchen: Kitchen, order: Order, pancakes: Dish, salad: Dish) -> None:
    assert kitchen.estimate_order_minutes(order) == 0
    assert kitchen.estimate_order_minutes(full_order(order, pancakes, salad)) == 10
    assert kitchen.station_loads() == {HOT_STATION: 0, COLD_STATION: 0}


def test_accept_order_creates_tickets_and_loads_stations(kitchen: Kitchen, order: Order, pancakes: Dish, salad: Dish) -> None:
    tickets = kitchen.accept_order(full_order(order, pancakes, salad), NOW)
    assert [ticket.station_name for ticket in tickets] == [HOT_STATION, COLD_STATION]
    assert order.status is OrderStatus.IN_PROGRESS
    assert kitchen.station_loads() == {HOT_STATION: 10, COLD_STATION: 5}
    assert kitchen.tickets_of(order.number) == tickets


def test_next_order_waits_for_the_queue(kitchen: Kitchen, order: Order, medium_table, waiter, adult_guest, pancakes: Dish) -> None:
    order.add_item(pancakes, 2)
    kitchen.accept_order(order, NOW)
    second = Order(2, medium_table, waiter, adult_guest, NOW)
    second.add_item(pancakes, 2)
    tickets = kitchen.accept_order(second, NOW)
    assert tickets[0].ready_in_minutes == 20


def test_overloaded_station_rolls_the_order_back(
    stocked_inventory: Inventory, cold_station: KitchenStation, order: Order, medium_table, waiter, adult_guest, pancakes: Dish, salad: Dish
) -> None:
    hot_cook = Cook("Ivan", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, station=HOT_STATION)
    busy_station = KitchenStation(HOT_STATION, 15)
    busy_station.add_cook(hot_cook)
    kitchen = Kitchen(stocked_inventory)
    kitchen.add_station(busy_station)
    kitchen.add_station(cold_station)
    order.add_item(pancakes, 2)
    kitchen.accept_order(order, NOW)
    second = full_order(Order(2, medium_table, waiter, adult_guest, NOW), salad, pancakes)
    with pytest.raises(KitchenOverloadError, match="превышает"):
        kitchen.accept_order(second, NOW)
    assert kitchen.station_loads() == {HOT_STATION: 10, COLD_STATION: 0}
    assert second.status is OrderStatus.NEW
    with pytest.raises(OrderNotFoundError):
        kitchen.tickets_of(2)


def test_order_with_missing_stock_is_not_accepted(
    hot_station: KitchenStation, cold_station: KitchenStation, order: Order, pancakes: Dish
) -> None:
    kitchen = Kitchen(Inventory())
    kitchen.add_station(hot_station)
    kitchen.add_station(cold_station)
    order.add_item(pancakes, 1)
    with pytest.raises(DishUnavailableError, match="не хватает продуктов"):
        kitchen.accept_order(order, NOW)
    assert order.status is OrderStatus.NEW


def test_finishing_all_tickets_makes_the_order_ready(
    kitchen: Kitchen, stocked_inventory: Inventory, order: Order, pancakes: Dish, salad: Dish, flour, tomato, today
) -> None:
    pancake_ticket, salad_ticket = kitchen.accept_order(full_order(order, pancakes, salad), NOW)
    kitchen.finish_ticket(pancake_ticket, NOW)
    assert order.status is OrderStatus.IN_PROGRESS
    kitchen.finish_ticket(salad_ticket, NOW)
    assert order.status is OrderStatus.READY
    assert stocked_inventory.total_of(flour, today) == pytest.approx(4800)
    assert stocked_inventory.total_of(tomato, today) == pytest.approx(4850)
    assert kitchen.station_loads() == {HOT_STATION: 0, COLD_STATION: 0}


def test_minutes_left_and_late_tickets(kitchen: Kitchen, order: Order, pancakes: Dish, salad: Dish) -> None:
    pancake_ticket, salad_ticket = kitchen.accept_order(full_order(order, pancakes, salad), NOW)
    assert kitchen.order_minutes_left(order.number, NOW + timedelta(minutes=4)) == 6
    assert kitchen.late_tickets(NOW + timedelta(minutes=7)) == [salad_ticket]
    assert len(kitchen.late_tickets(NOW + timedelta(minutes=11))) == 2
    kitchen.finish_ticket(pancake_ticket, NOW)
    kitchen.finish_ticket(salad_ticket, NOW)
    assert kitchen.order_minutes_left(order.number, NOW) == 0
    assert kitchen.late_tickets(NOW + timedelta(hours=1)) == []


def test_unknown_order_has_no_tickets(kitchen: Kitchen) -> None:
    with pytest.raises(OrderNotFoundError, match="99"):
        kitchen.tickets_of(99)
