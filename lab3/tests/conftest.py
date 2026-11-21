from datetime import date
from decimal import Decimal

import pytest

from restaurant.catalog.allergen import Allergen
from restaurant.catalog.ingredient import Ingredient
from restaurant.catalog.nutrition import NutritionInfo
from restaurant.guests.customer import Customer
from restaurant.inventory.inventory import Inventory
from restaurant.inventory.supplier import Supplier
from restaurant.menu.dish import Dish
from restaurant.menu.recipe import Recipe
from restaurant.staff.bartender import Bartender
from restaurant.staff.cashier import Cashier
from restaurant.staff.chef import Chef
from restaurant.staff.cook import Cook
from restaurant.staff.manager import ApprovalLimits, Manager
from restaurant.staff.waiter import Waiter
from tests.constants import ADULT_BIRTH, HIRED_ON, HOURLY_RATE, MINOR_BIRTH, PHONE, TODAY


@pytest.fixture
def today() -> date:
    return TODAY


@pytest.fixture
def flour() -> Ingredient:
    nutrition = NutritionInfo(3.6, 0.1, 0.01, 0.76)
    return Ingredient("flour", "g", nutrition, shelf_life_days=180, allergens=frozenset({Allergen.GLUTEN}))


@pytest.fixture
def milk() -> Ingredient:
    nutrition = NutritionInfo(0.6, 0.03, 0.03, 0.05)
    return Ingredient("milk", "ml", nutrition, shelf_life_days=7, allergens=frozenset({Allergen.MILK}), is_animal_origin=True)


@pytest.fixture
def tomato() -> Ingredient:
    return Ingredient("tomato", "g", NutritionInfo(0.2, 0.01, 0.0, 0.04), shelf_life_days=5)


@pytest.fixture
def inventory() -> Inventory:
    return Inventory()


@pytest.fixture
def supplier(flour: Ingredient, milk: Ingredient) -> Supplier:
    supplier = Supplier("Fresh Farm", "+375291112233", lead_time_days=2)
    supplier.set_price(flour, Decimal("0.002"))
    supplier.set_price(milk, Decimal("0.001"))
    return supplier


@pytest.fixture
def pancake_recipe(flour: Ingredient, milk: Ingredient) -> Recipe:
    recipe = Recipe(["Mix", "Fry"], cooking_minutes=10, portions=2)
    recipe.add_requirement(flour, 200)
    recipe.add_requirement(milk, 300)
    return recipe


@pytest.fixture
def salad_recipe(tomato: Ingredient) -> Recipe:
    recipe = Recipe(["Slice"], cooking_minutes=5)
    recipe.add_requirement(tomato, 150)
    return recipe


@pytest.fixture
def pancakes(pancake_recipe: Recipe) -> Dish:
    return Dish("Pancakes", Decimal("7.50"), pancake_recipe)


@pytest.fixture
def salad(salad_recipe: Recipe) -> Dish:
    return Dish("Tomato salad", Decimal("5.00"), salad_recipe)


@pytest.fixture
def waiter() -> Waiter:
    return Waiter("Anna", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, languages=["English", "Polish"])


@pytest.fixture
def chef() -> Chef:
    return Chef("Marco", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, cuisine="Italian")


@pytest.fixture
def cook() -> Cook:
    return Cook("Ivan", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, station="grill")


@pytest.fixture
def bartender() -> Bartender:
    return Bartender("Olga", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON)


@pytest.fixture
def cashier() -> Cashier:
    return Cashier("Nina", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, register_number=1)


@pytest.fixture
def manager() -> Manager:
    limits = ApprovalLimits(Decimal(15), Decimal(100), 6.0)
    return Manager("Boris", PHONE, ADULT_BIRTH, Decimal("20.00"), HIRED_ON, limits)


@pytest.fixture
def adult_guest() -> Customer:
    return Customer("Petr", PHONE, ADULT_BIRTH, "petr@example.com")


@pytest.fixture
def minor_guest() -> Customer:
    return Customer("Kolya", PHONE, MINOR_BIRTH, "kolya@example.com")
