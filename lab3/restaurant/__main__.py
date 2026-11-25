import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from restaurant.app import RestaurantApp
from restaurant.catalog.allergen import Allergen
from restaurant.catalog.ingredient import Ingredient
from restaurant.catalog.nutrition import NutritionInfo
from restaurant.delivery.courier import Courier
from restaurant.hall.table import Table
from restaurant.inventory.inventory import Inventory
from restaurant.inventory.storage import InventoryStorage
from restaurant.kitchen.kitchen import Kitchen
from restaurant.kitchen.kitchen_station import KitchenStation
from restaurant.menu.category import MenuCategory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu
from restaurant.menu.recipe import Recipe
from restaurant.staff.cashier import Cashier
from restaurant.staff.cook import Cook
from restaurant.staff.waiter import Waiter


def _create_demo_menu(today: date, inventory_path: Path | None = None) -> tuple[Menu, Inventory]:
    ingredient_data = {
        "Помидоры": (0.18, 0.009, 0.002, 0.039, 5, frozenset(), False),
        "Огурцы": (0.15, 0.007, 0.001, 0.036, 5, frozenset(), False),
        "Листья салата": (0.15, 0.014, 0.002, 0.029, 4, frozenset(), False),
        "Сыр фета": (2.65, 0.14, 0.21, 0.04, 10, frozenset({Allergen.MILK}), True),
        "Оливки": (1.15, 0.008, 0.11, 0.06, 30, frozenset(), False),
        "Курица": (1.65, 0.31, 0.036, 0.0, 3, frozenset(), True),
        "Сухарики": (4.0, 0.12, 0.08, 0.72, 30, frozenset({Allergen.GLUTEN}), False),
        "Пармезан": (4.3, 0.38, 0.29, 0.04, 20, frozenset({Allergen.MILK}), True),
        "Тунец": (1.3, 0.29, 0.01, 0.0, 2, frozenset({Allergen.FISH}), True),
        "Свёкла": (0.43, 0.016, 0.002, 0.096, 7, frozenset(), False),
        "Капуста": (0.25, 0.013, 0.001, 0.058, 7, frozenset(), False),
        "Картофель": (0.77, 0.02, 0.001, 0.17, 14, frozenset(), False),
        "Морковь": (0.41, 0.009, 0.002, 0.096, 10, frozenset(), False),
        "Лук": (0.4, 0.011, 0.001, 0.093, 10, frozenset(), False),
        "Грибы": (0.22, 0.031, 0.003, 0.033, 5, frozenset(), False),
        "Сливки": (3.4, 0.02, 0.35, 0.03, 7, frozenset({Allergen.MILK}), True),
        "Макароны": (3.7, 0.13, 0.015, 0.75, 180, frozenset({Allergen.GLUTEN}), False),
        "Бекон": (5.4, 0.37, 0.42, 0.015, 5, frozenset(), True),
        "Яйца": (1.43, 0.13, 0.095, 0.007, 20, frozenset({Allergen.EGGS}), True),
        "Мука": (3.64, 0.10, 0.01, 0.76, 180, frozenset({Allergen.GLUTEN}), False),
        "Сметана": (2.06, 0.03, 0.20, 0.04, 7, frozenset({Allergen.MILK}), True),
        "Рис": (3.6, 0.07, 0.007, 0.80, 180, frozenset(), False),
        "Рыба": (1.2, 0.20, 0.04, 0.0, 2, frozenset({Allergen.FISH}), True),
        "Кабачки": (0.17, 0.012, 0.003, 0.031, 5, frozenset(), False),
        "Творог": (1.21, 0.17, 0.05, 0.03, 7, frozenset({Allergen.MILK}), True),
        "Сахар": (3.87, 0.0, 0.0, 1.0, 365, frozenset(), False),
        "Яблоки": (0.52, 0.003, 0.002, 0.14, 14, frozenset(), False),
        "Сливочное масло": (7.17, 0.009, 0.81, 0.001, 30, frozenset({Allergen.MILK}), True),
        "Панировочные сухари": (3.95, 0.13, 0.05, 0.72, 90, frozenset({Allergen.GLUTEN}), False),
    }
    ingredients = {
        name: Ingredient(
            name, "г", NutritionInfo(*values[:4]), values[4], values[5], values[6]
        )
        for name, values in ingredient_data.items()
    }
    inventory = Inventory()
    storage = InventoryStorage(inventory_path) if inventory_path is not None else None
    loaded = storage.load(inventory, ingredients) if storage is not None else False
    if not loaded:
        for ingredient in ingredients.values():
            inventory.receive(ingredient, 5000, today)

    menu = Menu("Основное меню")
    categories = {
        name: MenuCategory(name)
        for name in ("Салаты", "Супы", "Горячие блюда", "Десерты")
    }
    dish_data = [
        (
            "Салаты", "Овощной салат", "8.50", 5,
            {"Помидоры": 150, "Огурцы": 100},
        ),
        (
            "Салаты", "Греческий салат", "12.00", 7,
            {"Помидоры": 100, "Огурцы": 80, "Сыр фета": 50, "Оливки": 25},
        ),
        (
            "Салаты", "Цезарь с курицей", "15.50", 12,
            {"Курица": 120, "Листья салата": 70, "Сухарики": 30, "Пармезан": 20},
        ),
        (
            "Салаты", "Салат с тунцом", "16.00", 8,
            {"Тунец": 100, "Листья салата": 60, "Огурцы": 60, "Яйца": 50},
        ),
        (
            "Супы", "Борщ", "13.00", 35,
            {"Свёкла": 100, "Капуста": 100, "Картофель": 100, "Морковь": 40, "Лук": 30},
        ),
        (
            "Супы", "Грибной крем-суп", "12.50", 25,
            {"Грибы": 120, "Картофель": 80, "Сливки": 60, "Лук": 25},
        ),
        (
            "Супы", "Куриный суп", "11.00", 30,
            {"Курица": 100, "Картофель": 80, "Морковь": 40, "Лук": 20},
        ),
        (
            "Горячие блюда", "Котлета с картофельным пюре", "18.50", 25,
            {
                "Курица": 140, "Панировочные сухари": 25, "Яйца": 30,
                "Картофель": 180, "Сливочное масло": 15,
            },
        ),
        (
            "Горячие блюда", "Паста карбонара", "19.00", 20,
            {"Макароны": 120, "Бекон": 60, "Яйца": 50, "Пармезан": 25},
        ),
        (
            "Горячие блюда", "Курица с рисом", "17.50", 25,
            {"Курица": 150, "Рис": 100, "Морковь": 30, "Лук": 20},
        ),
        (
            "Горячие блюда", "Драники со сметаной", "14.00", 20,
            {"Картофель": 220, "Яйца": 40, "Мука": 25, "Сметана": 40},
        ),
        (
            "Горячие блюда", "Рыба с овощами", "21.00", 22,
            {"Рыба": 150, "Кабачки": 80, "Помидоры": 70, "Лук": 20},
        ),
        (
            "Десерты", "Сырники", "10.50", 15,
            {"Творог": 150, "Яйца": 30, "Мука": 25, "Сахар": 15},
        ),
        (
            "Десерты", "Чизкейк", "13.50", 10,
            {
                "Творог": 100, "Сливки": 50, "Сахар": 25,
                "Сливочное масло": 20, "Сухарики": 25,
            },
        ),
        (
            "Десерты", "Яблочный штрудель", "11.50", 30,
            {"Яблоки": 120, "Мука": 60, "Сахар": 20, "Сливочное масло": 15},
        ),
    ]
    for category_name, name, price, minutes, requirements in dish_data:
        recipe = Recipe(
            ["Подготовить ингредиенты", "Приготовить блюдо", "Подать гостю"],
            minutes,
            station="универсальный цех",
        )
        for ingredient_name, amount in requirements.items():
            recipe.add_requirement(ingredients[ingredient_name], amount)
        categories[category_name].add_dish(Dish(name, Decimal(price), recipe))

    for category in categories.values():
        menu.add_category(category)
    return menu, inventory


def _create_demo_staff() -> tuple[Waiter, Cashier, Courier, Cook]:
    waiter = Waiter("Анна", "+375330000011", date(1995, 5, 12), Decimal("12.00"), date(2020, 1, 10))
    cashier = Cashier("Мария", "+375290000021", date(1992, 3, 8), Decimal("11.00"), date(2019, 6, 1), 1)
    courier = Courier("Иван", "+375330000031", date(1990, 7, 14), Decimal("10.00"), date(2022, 2, 1), "велосипед")
    cook = Cook("Сергей", "+375330000004", date(1993, 4, 2), Decimal("13.00"), date(2021, 3, 1), "универсальный цех")
    return waiter, cashier, courier, cook


def _create_demo_kitchen(inventory: Inventory, cook: Cook) -> Kitchen:
    kitchen = Kitchen(inventory)
    station = KitchenStation("универсальный цех", 60)
    station.add_cook(cook)
    kitchen.add_station(station)
    return kitchen


def create_demo_app(inventory_path: Path | None = None) -> RestaurantApp:
    today = date.today()
    menu, inventory = _create_demo_menu(today, inventory_path)
    waiter, cashier, courier, cook = _create_demo_staff()
    kitchen = _create_demo_kitchen(inventory, cook)
    return RestaurantApp(
        menu, inventory, waiter, Table(1, 4), today=today, cashier=cashier, couriers=[courier], kitchen=kitchen
    )


def _get_inventory_path() -> Path:
    if sys.platform == "win32":
        data_dir = Path(
            os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
        )
    elif sys.platform == "darwin":
        data_dir = Path.home() / "Library" / "Application Support"
    else:
        data_dir = Path(
            os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        )
    return data_dir / "RestaurantApp" / "inventory.json"


def main() -> None:
    inventory_path = _get_inventory_path()
    app = create_demo_app(inventory_path)
    storage = InventoryStorage(inventory_path)
    app.inventory.set_change_callback(lambda: storage.save(app.inventory))
    try:
        app.run()
    finally:
        storage.save(app.inventory)


if __name__ == "__main__":
    main()
