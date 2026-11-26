from datetime import date
from decimal import Decimal

import pytest

from restaurant.catalog.allergen import Allergen
from restaurant.catalog.ingredient import Ingredient
from restaurant.catalog.nutrition import NutritionInfo
from restaurant.guests.customer import Customer
from restaurant.inventory.inventory import Inventory
from restaurant.inventory.supplier import Supplier
from restaurant.hall.hall import Hall
from restaurant.hall.reservation_book import ReservationBook
from restaurant.hall.seating_planner import SeatingPlanner
from restaurant.hall.table import Table
from restaurant.hall.waitlist import Waitlist
from restaurant.kitchen.kitchen import Kitchen
from restaurant.kitchen.kitchen_station import KitchenStation
from restaurant.menu.dish import Dish
from restaurant.orders.order import Order
from restaurant.menu.recipe import Recipe
from restaurant.staff.bartender import Bartender
from restaurant.staff.cashier import Cashier
from restaurant.staff.chef import Chef
from restaurant.staff.cook import Cook
from restaurant.staff.manager import ApprovalLimits, Manager
from restaurant.staff.waiter import Waiter
from tests.constants import ADULT_BIRTH, COLD_STATION, HIRED_ON, HOT_STATION, HOURLY_RATE, MINOR_BIRTH, NOW, PHONE, TODAY


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
    recipe = Recipe(["Slice"], cooking_minutes=5, station=COLD_STATION)
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


@pytest.fixture
def gold_guest() -> Customer:
    return Customer("Gold", PHONE, ADULT_BIRTH, "gold@example.com")


@pytest.fixture
def small_table() -> Table:
    return Table(1, 2)


@pytest.fixture
def window_table() -> Table:
    return Table(2, 3, near_window=True)


@pytest.fixture
def medium_table() -> Table:
    return Table(3, 4)


@pytest.fixture
def big_table() -> Table:
    return Table(4, 8)


@pytest.fixture
def main_hall(small_table: Table, window_table: Table, medium_table: Table, big_table: Table) -> Hall:
    hall = Hall("Основной")
    for table in (small_table, window_table, medium_table, big_table):
        hall.add_table(table)
    return hall


@pytest.fixture
def book() -> ReservationBook:
    return ReservationBook()


@pytest.fixture
def waitlist() -> Waitlist:
    return Waitlist()


@pytest.fixture
def planner(main_hall: Hall, book: ReservationBook, waitlist: Waitlist) -> SeatingPlanner:
    return SeatingPlanner([main_hall], book, waitlist)


@pytest.fixture
def stocked_inventory(inventory: Inventory, flour: Ingredient, milk: Ingredient, tomato: Ingredient) -> Inventory:
    for ingredient in (flour, milk, tomato):
        inventory.receive(ingredient, 5000, TODAY)
    return inventory


@pytest.fixture
def order(medium_table: Table, waiter: Waiter, adult_guest: Customer) -> Order:
    return Order(1, medium_table, waiter, adult_guest, NOW)


@pytest.fixture
def hot_cook() -> Cook:
    return Cook("Ivan", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, station=HOT_STATION)


@pytest.fixture
def cold_cook() -> Cook:
    return Cook("Dasha", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, station=COLD_STATION)


@pytest.fixture
def hot_station(hot_cook: Cook) -> KitchenStation:
    station = KitchenStation(HOT_STATION, 60)
    station.add_cook(hot_cook)
    return station


@pytest.fixture
def cold_station(cold_cook: Cook) -> KitchenStation:
    station = KitchenStation(COLD_STATION, 60)
    station.add_cook(cold_cook)
    return station


@pytest.fixture
def kitchen(stocked_inventory: Inventory, hot_station: KitchenStation, cold_station: KitchenStation) -> Kitchen:
    kitchen = Kitchen(stocked_inventory)
    kitchen.add_station(hot_station)
    kitchen.add_station(cold_station)
    return kitchen
