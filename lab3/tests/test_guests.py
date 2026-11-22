from datetime import date
from decimal import Decimal

import pytest

from restaurant.catalog.allergen import Allergen
from restaurant.exceptions import InsufficientPointsError, InvalidDataError
from restaurant.guests.customer import REGULAR_VISITS, Customer
from restaurant.guests.loyalty import LoyaltyCard, LoyaltyTier
from restaurant.guests.profile import GuestProfile
from restaurant.menu.dish import Dish
from tests.constants import ADULT_BIRTH, PHONE


def card_with_lifetime_points(points: int, today: date) -> LoyaltyCard:
    card = LoyaltyCard("C-1", today)
    card.earn_points(Decimal(points * 10))
    return card


def test_earn_and_redeem_points(today: date) -> None:
    card = LoyaltyCard("C-1", today)
    assert card.earn_points(Decimal(1000)) == 100
    card.redeem_points(40)
    assert (card.balance, card.lifetime_points) == (60, 100)
    with pytest.raises(InsufficientPointsError):
        card.redeem_points(61)
    with pytest.raises(InvalidDataError):
        card.redeem_points(0)


def test_card_number_required(today: date) -> None:
    with pytest.raises(InvalidDataError):
        LoyaltyCard(" ", today)


def test_tiers_and_discounts(today: date) -> None:
    assert card_with_lifetime_points(100, today).tier() is LoyaltyTier.BRONZE
    silver = card_with_lifetime_points(500, today)
    assert silver.tier() is LoyaltyTier.SILVER
    assert silver.discount_percent() == Decimal(5)
    gold = card_with_lifetime_points(2000, today)
    assert gold.tier() is LoyaltyTier.GOLD
    assert gold.discount_percent() == Decimal(10)


def test_points_to_next_tier(today: date) -> None:
    assert card_with_lifetime_points(100, today).points_to_next_tier() == 400
    assert card_with_lifetime_points(500, today).points_to_next_tier() == 1500
    assert card_with_lifetime_points(2000, today).points_to_next_tier() == 0


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


def test_customer_loyalty_card(adult_guest: Customer, today: date) -> None:
    assert adult_guest.discount_percent() == Decimal(0)
    assert adult_guest.earn_loyalty_points(Decimal(100)) == 0
    adult_guest.attach_card(card_with_lifetime_points(500, today))
    assert adult_guest.discount_percent() == Decimal(5)
    assert adult_guest.earn_loyalty_points(Decimal(100)) == 10
    with pytest.raises(InvalidDataError):
        adult_guest.attach_card(LoyaltyCard("C-2", today))


def test_customer_can_eat_uses_profile(pancakes: Dish) -> None:
    guest = Customer("Petr", PHONE, ADULT_BIRTH, "petr@example.com", GuestProfile([Allergen.MILK]))
    assert not guest.can_eat(pancakes)
