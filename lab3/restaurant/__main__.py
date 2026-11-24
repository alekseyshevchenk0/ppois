from datetime import date
from decimal import Decimal

from lab3.restaurant.app import RestaurantApp
from restaurant.catalog.ingredient import Ingredient
from restaurant.catalog.nutrition import NutritionInfo
from restaurant.inventory.inventory import Inventory
from restaurant.menu.category import MenuCategory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu
from restaurant.menu.recipe import Recipe
from restaurant.staff.waiter import Waiter
from restaurant.hall.table import Table


def create_demo_app() -> RestaurantApp:
    today = date.today()
    tomatoes = Ingredient("Помидоры", "г", NutritionInfo(0.2, 0.01, 0.0, 0.04), 5)
    cucumbers = Ingredient("Огурцы", "г", NutritionInfo(0.15, 0.01, 0.0, 0.03), 5)
    inventory = Inventory()
    inventory.receive(tomatoes, 3000, today)
    inventory.receive(cucumbers, 3000, today)
    salad_recipe = Recipe(["Нарезать овощи", "Смешать ингредиенты"], 5, station="холодный цех")
    salad_recipe.add_requirement(tomatoes, 150)
    salad_recipe.add_requirement(cucumbers, 100)
    salad = Dish("Овощной салат", Decimal("6.50"), salad_recipe)
    menu = Menu("Основное меню")
    category = MenuCategory("Салаты")
    category.add_dish(salad)
    menu.add_category(category)
    waiter = Waiter("Анна", "+375330000000", date(1995, 5, 12), Decimal("12.00"), date(2020, 1, 10))
    return RestaurantApp(menu, inventory, waiter, Table(1, 4), today=today)


def main() -> None:
    create_demo_app().run()


if __name__ == "__main__":
    main()
