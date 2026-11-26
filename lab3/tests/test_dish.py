from datetime import date
from decimal import Decimal

import pytest

from restaurant.catalog.allergen import Allergen
from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import AllergenConflictError, DishUnavailableError, InvalidDataError
from restaurant.inventory.inventory import Inventory
from restaurant.menu.dish import DEFAULT_FRESHNESS_DAYS, Dish
from restaurant.menu.recipe import Recipe


def test_dish_validation(salad_recipe: Recipe) -> None:
    with pytest.raises(InvalidDataError):
        Dish("", Decimal("5"), salad_recipe)
    with pytest.raises(InvalidDataError):
        Dish("Salad", Decimal("0"), salad_recipe)


def test_price_change_rounds_to_cents(pancakes: Dish) -> None:
    assert pancakes.change_price_by_percent(Decimal("10")) == Decimal("8.25")
    assert pancakes.change_price_by_percent(Decimal("-50")) == Decimal("4.12")
    with pytest.raises(InvalidDataError):
        pancakes.change_price_by_percent(Decimal("-100"))


def test_dish_properties_come_from_recipe(pancakes: Dish, salad: Dish) -> None:
    assert pancakes.allergens() == {Allergen.GLUTEN, Allergen.MILK}
    assert salad.is_vegetarian()
    assert pancakes.nutrition().calories > 0


def test_ensure_safe_for(pancakes: Dish) -> None:
    pancakes.ensure_safe_for([Allergen.NUTS])
    with pytest.raises(AllergenConflictError) as error:
        pancakes.ensure_safe_for([Allergen.MILK, Allergen.NUTS])
    assert error.value.allergen_names == "молоко"


def test_availability_depends_on_stock_and_stop_flag(
    pancakes: Dish, inventory: Inventory, flour: Ingredient, milk: Ingredient, today: date
) -> None:
    assert not pancakes.is_available(inventory, today)
    inventory.receive(flour, 500, today)
    inventory.receive(milk, 500, today)
    assert pancakes.is_available(inventory, today)
    pancakes.stop()
    assert not pancakes.is_available(inventory, today)
    pancakes.resume()
    assert pancakes.is_available(inventory, today)


def test_cook_consumes_one_portion(
    pancakes: Dish, inventory: Inventory, flour: Ingredient, milk: Ingredient, today: date
) -> None:
    inventory.receive(flour, 500, today)
    inventory.receive(milk, 500, today)
    pancakes.cook(inventory, today)
    assert inventory.total_of(flour, today) == pytest.approx(400)
    assert inventory.total_of(milk, today) == pytest.approx(350)


def test_cook_fails_when_stopped_or_missing(pancakes: Dish, inventory: Inventory, today: date) -> None:
    with pytest.raises(DishUnavailableError, match="не хватает ингредиентов: flour, milk"):
        pancakes.cook(inventory, today)
    pancakes.stop()
    with pytest.raises(DishUnavailableError, match="стоп-листе"):
        pancakes.cook(inventory, today)


def test_days_until_stock_expires(
    pancakes: Dish, inventory: Inventory, flour: Ingredient, milk: Ingredient, today: date
) -> None:
    assert pancakes.days_until_stock_expires(inventory, today) == DEFAULT_FRESHNESS_DAYS
    inventory.receive(flour, 500, today)
    inventory.receive(milk, 500, today)
    assert pancakes.days_until_stock_expires(inventory, today) == 7
