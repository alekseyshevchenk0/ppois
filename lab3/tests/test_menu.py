from datetime import date
from decimal import Decimal

import pytest

from restaurant.catalog.allergen import Allergen
from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InvalidDataError
from restaurant.inventory.inventory import Inventory
from restaurant.menu.category import MenuCategory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu


@pytest.fixture
def mains(pancakes: Dish) -> MenuCategory:
    category = MenuCategory("Mains")
    category.add_dish(pancakes)
    return category


@pytest.fixture
def starters(salad: Dish) -> MenuCategory:
    category = MenuCategory("Starters")
    category.add_dish(salad)
    return category


@pytest.fixture
def menu(mains: MenuCategory, starters: MenuCategory) -> Menu:
    menu = Menu("Autumn")
    menu.add_category(mains)
    menu.add_category(starters)
    return menu


def test_category_add_find_remove(pancakes: Dish, salad: Dish) -> None:
    category = MenuCategory("Mains")
    category.add_dish(pancakes)
    with pytest.raises(InvalidDataError):
        category.add_dish(pancakes)
    assert category.find_dish("Pancakes") is pancakes
    assert category.remove_dish("Pancakes") is pancakes
    assert category.find_dish("Pancakes") is None
    with pytest.raises(InvalidDataError):
        category.remove_dish("Pancakes")
    assert category.dishes == ()


def test_category_name_required() -> None:
    with pytest.raises(InvalidDataError):
        MenuCategory(" ")


def test_category_price_statistics(pancakes: Dish, salad: Dish) -> None:
    category = MenuCategory("Mixed")
    assert category.average_price() == Decimal(0)
    assert category.cheapest_dish() is None
    category.add_dish(pancakes)
    category.add_dish(salad)
    assert category.average_price() == Decimal("6.25")
    assert category.cheapest_dish() is salad


def test_category_available_dishes(
    mains: MenuCategory, pancakes: Dish, inventory: Inventory, flour: Ingredient, milk: Ingredient, today: date
) -> None:
    assert mains.available_dishes(inventory, today) == []
    inventory.receive(flour, 500, today)
    inventory.receive(milk, 500, today)
    assert mains.available_dishes(inventory, today) == [pancakes]


def test_menu_structure(menu: Menu, mains: MenuCategory) -> None:
    assert menu.category("Mains") is mains
    with pytest.raises(InvalidDataError):
        menu.category("Desserts")
    with pytest.raises(InvalidDataError):
        menu.add_category(MenuCategory("Mains"))
    with pytest.raises(InvalidDataError):
        Menu("")


def test_menu_lookup(menu: Menu, pancakes: Dish) -> None:
    assert len(menu.all_dishes()) == 2
    assert menu.find_dish("Pancakes") is pancakes
    assert menu.find_dish("Pizza") is None


def test_auto_stop_list_explains_missing_ingredients(
    menu: Menu, inventory: Inventory, tomato: Ingredient, flour: Ingredient, milk: Ingredient, today: date
) -> None:
    inventory.receive(tomato, 1000, today)
    inventory.receive(flour, 500, today)
    report = menu.stop_list(inventory, today)
    assert list(report) == ["Pancakes"]
    assert report["Pancakes"] == {milk: pytest.approx(150)}


def test_menu_available_dishes_follow_stock(
    menu: Menu, salad: Dish, inventory: Inventory, tomato: Ingredient, today: date
) -> None:
    inventory.receive(tomato, 150, today)
    assert menu.available_dishes(inventory, today) == [salad]
    salad.cook(inventory, today)
    assert menu.available_dishes(inventory, today) == []


def test_menu_filters(menu: Menu, pancakes: Dish, salad: Dish) -> None:
    assert menu.dishes_safe_for([Allergen.MILK]) == [salad]
    assert menu.vegetarian_dishes() == [salad]
    assert menu.dishes_in_price_range(Decimal("6"), Decimal("10")) == [pancakes]
    assert menu.most_expensive_dish() is pancakes
    assert Menu("Empty").most_expensive_dish() is None
