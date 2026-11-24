from datetime import date
from decimal import Decimal

from restaurant.app import RestaurantApp
from restaurant.catalog.ingredient import Ingredient
from restaurant.catalog.nutrition import NutritionInfo
from restaurant.delivery.courier import Courier
from restaurant.hall.table import Table
from restaurant.inventory.inventory import Inventory
from restaurant.kitchen.kitchen import Kitchen
from restaurant.kitchen.kitchen_station import KitchenStation
from restaurant.menu.category import MenuCategory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu
from restaurant.menu.recipe import Recipe
from restaurant.staff.cashier import Cashier
from restaurant.staff.cook import Cook
from restaurant.staff.waiter import Waiter


def _create_demo_menu(today: date) -> tuple[Menu, Inventory]:
    tomatoes = Ingredient("Помидоры", "г", NutritionInfo(0.2, 0.01, 0.0, 0.04), 5)
    cucumbers = Ingredient("Огурцы", "г", NutritionInfo(0.15, 0.01, 0.0, 0.03), 5)
    inventory = Inventory()
    inventory.receive(tomatoes, 3000, today)
    inventory.receive(cucumbers, 3000, today)
    recipe = Recipe(["Нарезать овощи", "Смешать ингредиенты"], 5, station="холодный цех")
    recipe.add_requirement(tomatoes, 150)
    recipe.add_requirement(cucumbers, 100)
    dish = Dish("Овощной салат", Decimal("6.50"), recipe)
    category = MenuCategory("Салаты")
    category.add_dish(dish)
    menu = Menu("Основное меню")
    menu.add_category(category)
    return menu, inventory


def _create_demo_staff() -> tuple[Waiter, Cashier, Courier, Cook]:
    waiter = Waiter("Анна", "+70000000001", date(1995, 5, 12), Decimal("12.00"), date(2020, 1, 10))
    cashier = Cashier("Мария", "+70000000002", date(1992, 3, 8), Decimal("11.00"), date(2019, 6, 1), 1)
    courier = Courier("Иван", "+70000000003", date(1990, 7, 14), Decimal("10.00"), date(2022, 2, 1), "велосипед")
    cook = Cook("Сергей", "+70000000004", date(1993, 4, 2), Decimal("13.00"), date(2021, 3, 1), "холодный цех")
    return waiter, cashier, courier, cook


def _create_demo_kitchen(inventory: Inventory, cook: Cook) -> Kitchen:
    kitchen = Kitchen(inventory)
    station = KitchenStation("холодный цех", 60)
    station.add_cook(cook)
    kitchen.add_station(station)
    return kitchen


def create_demo_app() -> RestaurantApp:
    today = date.today()
    menu, inventory = _create_demo_menu(today)
    waiter, cashier, courier, cook = _create_demo_staff()
    kitchen = _create_demo_kitchen(inventory, cook)
    return RestaurantApp(
        menu, inventory, waiter, Table(1, 4), today=today, cashier=cashier, couriers=[courier], kitchen=kitchen
    )


def main() -> None:
    create_demo_app().run()


if __name__ == "__main__":
    main()
