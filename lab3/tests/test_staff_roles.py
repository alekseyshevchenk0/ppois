from datetime import date, time
from decimal import Decimal

import pytest

from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import EmployeeNotAvailableError, InvalidDataError, UnderageGuestError
from restaurant.guests.customer import Customer
from restaurant.inventory.inventory import Inventory
from restaurant.menu.category import MenuCategory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu
from restaurant.staff.bartender import Bartender
from restaurant.staff.cashier import Cashier
from restaurant.staff.chef import Chef
from restaurant.staff.cook import Cook
from restaurant.staff.employee import Employee
from restaurant.staff.manager import Manager
from restaurant.staff.schedule import Schedule
from restaurant.staff.waiter import Waiter
from tests.constants import ADULT_BIRTH, HIRED_ON, HOURLY_RATE, PHONE


def test_employee_rate_must_be_positive() -> None:
    with pytest.raises(InvalidDataError):
        Employee("Ann", PHONE, ADULT_BIRTH, Decimal(0), HIRED_ON)


def test_years_of_service_and_raise(cook: Cook, today: date) -> None:
    assert cook.years_of_service(today) == 2
    assert cook.give_raise(Decimal(10)) == Decimal("11.00")
    with pytest.raises(InvalidDataError):
        cook.give_raise(Decimal(0))


def test_dismiss_and_reinstate(cook: Cook) -> None:
    cook.dismiss()
    with pytest.raises(EmployeeNotAvailableError):
        cook.ensure_active()
    cook.reinstate()
    cook.ensure_active()


def test_waiter_languages_and_tips(waiter: Waiter) -> None:
    assert waiter.speaks("english")
    assert not waiter.speaks("French")
    assert waiter.average_tip_per_guest() == Decimal(0)
    waiter.serve_guests(6)
    waiter.receive_tip(Decimal(30))
    assert waiter.average_tip_per_guest() == Decimal(5)
    with pytest.raises(InvalidDataError):
        waiter.receive_tip(Decimal(0))


def test_dismissed_waiter_cannot_serve(waiter: Waiter) -> None:
    waiter.dismiss()
    with pytest.raises(EmployeeNotAvailableError):
        waiter.serve_guests(2)


def test_cook_validation(cook: Cook) -> None:
    with pytest.raises(InvalidDataError):
        Cook("Ivan", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, station=" ")
    with pytest.raises(InvalidDataError):
        Cook("Ivan", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, station="grill", skill_level=6)
    with pytest.raises(InvalidDataError):
        cook.move_to_station("")


def test_cook_station(cook: Cook) -> None:
    assert cook.can_work_station("grill")
    cook.move_to_station("cold")
    assert cook.can_work_station("cold")
    assert not cook.can_work_station("grill")


def test_cook_skill_changes_speed(cook: Cook) -> None:
    assert cook.speed_factor() == pytest.approx(1.0)
    assert cook.adjusted_minutes(10) == 10
    cook.promote()
    cook.promote()
    assert cook.speed_factor() == pytest.approx(0.8)
    assert cook.adjusted_minutes(10) == 8
    with pytest.raises(InvalidDataError):
        cook.promote()


def test_beginner_cook_is_slower() -> None:
    beginner = Cook("Ivan", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, station="grill", skill_level=1)
    assert beginner.adjusted_minutes(10) > 10


def test_bartender_serves_alcohol_only_to_adults(bartender: Bartender, adult_guest: Customer, minor_guest: Customer, today: date) -> None:
    bartender.serve_drink(adult_guest, today, alcoholic=True)
    bartender.serve_drink(minor_guest, today)
    assert bartender.drinks_made == 2
    with pytest.raises(UnderageGuestError):
        bartender.serve_drink(minor_guest, today, alcoholic=True)
    assert bartender.drinks_made == 2


def test_uncertified_bartender_cannot_serve_alcohol(adult_guest: Customer, today: date) -> None:
    bartender = Bartender("Olga", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, is_alcohol_certified=False)
    assert not bartender.can_serve_alcohol_to(adult_guest, today)
    with pytest.raises(EmployeeNotAvailableError):
        bartender.serve_drink(adult_guest, today, alcoholic=True)


def test_bartender_can_serve_checks(bartender: Bartender, adult_guest: Customer, minor_guest: Customer, today: date) -> None:
    assert bartender.can_serve_alcohol_to(adult_guest, today)
    assert not bartender.can_serve_alcohol_to(minor_guest, today)


def test_cashier_till(cashier: Cashier) -> None:
    cashier.accept_cash(Decimal(50))
    cashier.give_change(Decimal(20))
    assert cashier.cash_in_till == Decimal(30)
    with pytest.raises(InvalidDataError):
        cashier.give_change(Decimal(100))
    assert cashier.close_till() == Decimal(30)
    assert (cashier.cash_in_till, cashier.transactions_count) == (Decimal(0), 0)


def test_cashier_register_number_must_be_positive() -> None:
    with pytest.raises(InvalidDataError):
        Cashier("Nina", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, register_number=0)


def test_manager_limits(manager: Manager) -> None:
    assert manager.can_approve_discount(Decimal(15))
    assert not manager.can_approve_discount(Decimal(16))
    assert manager.can_approve_refund(Decimal(100))
    assert not manager.can_approve_refund(Decimal(101))
    assert manager.approve_overtime(6.0)
    assert not manager.approve_overtime(7.0)
    assert manager.approvals_count == 1


def test_manager_assigns_shift(manager: Manager, waiter: Waiter, today: date) -> None:
    schedule = Schedule()
    shift = manager.assign_shift(schedule, waiter, today, time(9), time(17))
    assert schedule.shifts_of(waiter) == [shift]
    assert manager.approvals_count == 1


def test_chef_cuisine_required() -> None:
    with pytest.raises(InvalidDataError):
        Chef("Marco", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, cuisine="")


def test_chef_approval(chef: Chef, pancakes: Dish) -> None:
    assert not chef.has_approved(pancakes)
    chef.approve(pancakes)
    assert chef.has_approved(pancakes)
    chef.revoke(pancakes)
    assert not chef.has_approved(pancakes)


def test_chef_special_uses_ingredients_that_spoil_first(
    chef: Chef, pancakes: Dish, salad: Dish, inventory: Inventory, flour: Ingredient, milk: Ingredient, tomato: Ingredient, today: date
) -> None:
    category = MenuCategory("All")
    category.add_dish(pancakes)
    category.add_dish(salad)
    menu = Menu("Day")
    menu.add_category(category)
    for ingredient in (flour, milk, tomato):
        inventory.receive(ingredient, 500, today)
    assert chef.suggest_special(menu, inventory, today) is None
    chef.approve(pancakes)
    assert chef.suggest_special(menu, inventory, today) is pancakes
    chef.approve(salad)
    assert chef.suggest_special(menu, inventory, today) is salad
