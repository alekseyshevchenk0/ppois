from datetime import date
from decimal import Decimal

from lab3.restaurant.__main__ import create_demo_app
from lab3.restaurant.app import RestaurantApp
from restaurant.analytics.menu_recommender import MenuRecommender
from restaurant.catalog.ingredient import Ingredient
from restaurant.catalog.nutrition import NutritionInfo
from restaurant.inventory.inventory import Inventory
from restaurant.menu.category import MenuCategory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu
from restaurant.menu.recipe import Recipe
from restaurant.staff.waiter import Waiter
from restaurant.hall.table import Table


class ConsoleStub:
    def __init__(self, answers: list[str]) -> None:
        self.answers = iter(answers)
        self.messages: list[str] = []

    def input(self, prompt: str) -> str:
        self.messages.append(prompt)
        return next(self.answers)

    def output(self, message: str) -> None:
        self.messages.append(message)


def build_app(console: ConsoleStub) -> RestaurantApp:
    today = date(2026, 11, 24)
    ingredient = Ingredient("Огурец", "г", NutritionInfo(1, 0, 0, 0), 5)
    inventory = Inventory()
    inventory.receive(ingredient, 1000, today)
    recipe = Recipe(["Нарезать"], 5)
    recipe.add_requirement(ingredient, 100)
    dish = Dish("Салат", Decimal("5.00"), recipe)
    category = MenuCategory("Салаты")
    category.add_dish(dish)
    menu = Menu("Основное меню")
    menu.add_category(category)
    waiter = Waiter("Анна", "+375330000001", date(1995, 1, 1), Decimal("10"), date(2020, 1, 1))
    return RestaurantApp(menu, inventory, waiter, Table(1, 4), today, console.input, console.output)


def test_run_shows_menu_and_exits() -> None:
    console = ConsoleStub(["0"])
    build_app(console).run()
    assert any("ГЛАВНОЕ МЕНЮ" in message for message in console.messages)
    assert "Работа программы завершена" in console.messages


def test_show_dishes_and_available_dishes() -> None:
    console = ConsoleStub(["1", "2", "0"])
    build_app(console).run()
    assert sum("Салат" in message for message in console.messages) == 2


def test_show_inventory() -> None:
    console = ConsoleStub(["3", "0"])
    build_app(console).run()
    assert any("Огурец: 1000 г" in message for message in console.messages)


def test_create_order_and_list_it() -> None:
    console = ConsoleStub(["4", "1", "2", "Иван", "5", "0"])
    app = build_app(console)
    app.run()
    assert len(app.orders) == 1
    assert app.orders[0].subtotal() == Decimal("10.00")
    assert any("Заказ №1 создан" in message for message in console.messages)
    assert any("гость: Иван" in message for message in console.messages)


def test_create_order_rejects_invalid_dish_number() -> None:
    console = ConsoleStub(["4", "9", "0"])
    build_app(console).run()
    assert "Блюда с таким номером нет" in console.messages


def test_create_order_rejects_non_positive_quantity() -> None:
    console = ConsoleStub(["4", "1", "0", "0"])
    build_app(console).run()
    assert "Количество порций должно быть положительным." in console.messages


def test_recommendations_and_dynamic_prices() -> None:
    console = ConsoleStub(["6", "Пётр", "7", "0"])
    build_app(console).run()
    assert any("Рекомендации для гостя" in message for message in console.messages)
    assert any(message.startswith("Салат: ") and message.endswith(" руб.") for message in console.messages)


def test_invalid_choice_and_non_integer_input() -> None:
    console = ConsoleStub(["abc", "99", "0"])
    build_app(console).run()
    assert "Нужно ввести целое число" in console.messages
    assert "Неизвестный пункт меню. Повторите ввод" in console.messages


def test_demo_application_is_configured() -> None:
    app = create_demo_app()
    assert app.menu.name == "Основное меню"
    assert len(app.menu.all_dishes()) == 1
    assert app.inventory.stock_report(app.today)


def test_empty_inventory_and_empty_menu_messages() -> None:
    console = ConsoleStub(["2", "3", "4", "7", "0"])
    app = build_app(console)
    app.inventory = Inventory()
    app.menu = Menu("Пустое меню")
    app.run()
    assert "Список пуст" in console.messages
    assert "Склад пока пуст" in console.messages
    assert "Сейчас нет доступных блюд для заказа" in console.messages
    assert "Нет доступных блюд для расчёта цен" in console.messages


def test_empty_orders_and_empty_recommendations() -> None:
    console = ConsoleStub(["5", "6", "   ", "0"])
    app = build_app(console)
    app.menu = Menu("Пустое меню")
    app.recommender = MenuRecommender(app.menu)
    app.run()
    assert "Заказов пока нет" in console.messages
    assert "Рекомендации для гостя:" in console.messages
    assert "Список пуст" in console.messages


def test_empty_guest_name_does_not_create_order() -> None:
    console = ConsoleStub(["4", "1", "1", "   ", "0"])
    app = build_app(console)
    app.run()
    assert not app.orders
    assert "Имя гостя не должно быть пустым" in console.messages


def test_dispatch_displays_domain_errors() -> None:
    from restaurant.exceptions import InvalidDataError

    console = ConsoleStub([])
    app = build_app(console)

    def fail() -> None:
        raise InvalidDataError("Проверка ошибки")

    app._show_dishes = fail
    app._dispatch(1)
    assert "Ошибка: Проверка ошибки" in console.messages
