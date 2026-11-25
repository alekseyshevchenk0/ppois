from decimal import Decimal

import pytest

from restaurant.catalog.allergen import Allergen
from restaurant.exceptions import InvalidDataError
from restaurant.guests.customer import REGULAR_VISITS, Customer
from restaurant.guests.profile import GuestProfile
from restaurant.menu.dish import Dish
from tests.constants import ADULT_BIRTH, PHONE


def test_profile_accepts_dish(pancakes: Dish, salad: Dish) -> None:
    assert GuestProfile().accepts(pancakes)
    assert not GuestProfile([Allergen.GLUTEN]).accepts(pancakes)
    assert not GuestProfile(is_vegetarian=True).accepts(pancakes)
    assert GuestProfile(is_vegetarian=True).accepts(salad)
    assert not GuestProfile(max_dish_price=Decimal("6")).accepts(pancakes)
    assert GuestProfile(max_dish_price=Decimal("6")).accepts(salad)


def test_profile_allergen_management(pancakes: Dish) -> None:
    profile = GuestProfile()
    profile.add_allergen(Allergen.MILK)
    assert not profile.accepts(pancakes)
    profile.remove_allergen(Allergen.MILK)
    assert profile.accepts(pancakes)


def test_profile_favorites() -> None:
    profile = GuestProfile()
    profile.record_order("Soup", 2)
    profile.record_order("Steak")
    profile.record_order("Pasta")
    profile.record_order("Steak")
    assert profile.times_ordered("Steak") == 2
    assert profile.times_ordered("Cake") == 0
    assert profile.favorites(2) == ["Soup", "Steak"]
    with pytest.raises(InvalidDataError):
        profile.record_order("Soup", 0)


def test_customer_email_validation() -> None:
    with pytest.raises(InvalidDataError):
        Customer("Petr", PHONE, ADULT_BIRTH, "not-an-email")


def test_regular_customer(adult_guest: Customer) -> None:
    for _ in range(REGULAR_VISITS - 1):
        adult_guest.register_visit()
    assert not adult_guest.is_regular()
    adult_guest.register_visit()
    assert adult_guest.is_regular()


def test_customer_can_eat_uses_profile(pancakes: Dish) -> None:
    guest = Customer("Petr", PHONE, ADULT_BIRTH, "petr@example.com", GuestProfile([Allergen.MILK]))
    assert not guest.can_eat(pancakes)
