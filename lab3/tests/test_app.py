from datetime import date
from decimal import Decimal

from restaurant.__main__ import create_demo_app
from restaurant.app import RestaurantApp
from restaurant.analytics.menu_recommender import MenuRecommender
from restaurant.delivery.courier import Courier
from restaurant.catalog.ingredient import Ingredient
from restaurant.catalog.nutrition import NutritionInfo
from restaurant.inventory.inventory import Inventory
from restaurant.kitchen.kitchen import Kitchen
from restaurant.kitchen.kitchen_station import KitchenStation
from restaurant.menu.category import MenuCategory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu
from restaurant.menu.recipe import Recipe
from restaurant.staff.waiter import Waiter
from restaurant.staff.cook import Cook
from restaurant.staff.cashier import Cashier
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


def _build_test_menu(today: date) -> tuple[Menu, Inventory]:
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
    return menu, inventory


def _build_test_staff(inventory: Inventory) -> tuple[Waiter, Cashier, Courier, Kitchen]:
    waiter = Waiter("Анна", "+70000000001", date(1995, 1, 1), Decimal("10"), date(2020, 1, 1))
    cashier = Cashier("Мария", "+70000000002", date(1992, 3, 8), Decimal("11"), date(2019, 6, 1), 1)
    courier = Courier("Иван", "+70000000003", date(1990, 7, 14), Decimal("10"), date(2022, 2, 1), "велосипед")
    cook = Cook("Сергей", "+70000000004", date(1993, 4, 2), Decimal("13"), date(2021, 3, 1), "горячий цех")
    kitchen = Kitchen(inventory)
    station = KitchenStation("горячий цех", 60)
    station.add_cook(cook)
    kitchen.add_station(station)
    return waiter, cashier, courier, kitchen


def build_app(console: ConsoleStub) -> RestaurantApp:
    today = date(2026, 11, 24)
    menu, inventory = _build_test_menu(today)
    waiter, cashier, courier, kitchen = _build_test_staff(inventory)
    return RestaurantApp(menu, inventory, waiter, Table(1, 4), today, console.input, console.output,
                         cashier, [courier], kitchen)


def test_run_shows_menu_and_exits() -> None:
    console = ConsoleStub(["0"])
    build_app(console).run()
    assert any("ГЛАВНОЕ МЕНЮ" in message for message in console.messages)
    assert "Работа программы завершена." in console.messages


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
    assert "Блюда с таким номером нет." in console.messages


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
    assert "Нужно ввести целое число." in console.messages
    assert "Неизвестный пункт меню. Повторите ввод." in console.messages


def test_demo_application_is_configured() -> None:
    app = create_demo_app()
    assert app.menu.name == "Основное меню"
    assert len(app.menu.all_dishes()) == 15
    assert len(app.menu.available_dishes(app.inventory, app.today)) == 15
    assert app.inventory.stock_report(app.today)


def test_empty_inventory_and_empty_menu_messages() -> None:
    console = ConsoleStub(["2", "3", "4", "7", "0"])
    app = build_app(console)
    app.inventory = Inventory()
    app.menu = Menu("Пустое меню")
    app.run()
    assert "Список пуст." in console.messages
    assert "Склад пока пуст." in console.messages
    assert "Сейчас нет доступных блюд для заказа." in console.messages
    assert "Нет доступных блюд для расчёта цен." in console.messages


def test_empty_orders_and_empty_recommendations() -> None:
    console = ConsoleStub(["5", "6", "   ", "0"])
    app = build_app(console)
    app.menu = Menu("Пустое меню")
    app.recommender = MenuRecommender(app.menu)
    app.run()
    assert "Заказов пока нет." in console.messages
    assert "Рекомендации для гостя:" in console.messages
    assert "Список пуст." in console.messages


def test_empty_guest_name_does_not_create_order() -> None:
    console = ConsoleStub(["4", "1", "1", "   ", "0"])
    app = build_app(console)
    app.run()
    assert not app.orders
    assert "Имя гостя не должно быть пустым." in console.messages


def test_dispatch_displays_domain_errors() -> None:
    from restaurant.exceptions import InvalidDataError

    console = ConsoleStub([])
    app = build_app(console)

    def fail() -> None:
        raise InvalidDataError("Проверка ошибки")

    app._show_dishes = fail
    app._dispatch(1)
    assert "Ошибка: Проверка ошибки" in console.messages


def test_order_lifecycle_and_card_payment():
    console = ConsoleStub(["4", "1", "1", "Иван", "8", "1", "8", "1", "8", "1", "9", "1", "2", "0"])
    app = build_app(console)
    app.run()
    assert app.orders[0].status.value == "оплачен"
    assert len(app.payments) == 1
    assert app.inventory.total_of(next(iter(app.inventory._batches)).ingredient, app.today) == 900
    assert app.kitchen.tickets_of(1)[0].is_done
    assert "Заказ подан гостю." in console.messages
    assert "Способ оплаты: карта" in console.messages


def test_reservation_creation_and_listing():
    console = ConsoleStub(["10", "Пётр", "2", "2026-11-25 19:00", "15", "1", "0"])
    app = build_app(console)
    app.run()
    assert len(app.reservations) == 1
    assert app.reservations[0].guests_count == 2
    assert any("Пётр" in message for message in console.messages)


def test_review_creation_and_display():
    console = ConsoleStub(["11", "1", "1", "Анна", "5", "Очень вкусно", "11", "2", "0"])
    app = build_app(console)
    app.run()
    assert len(app.reviews) == 1
    assert app.reviews[0].is_visible()
    assert any("Очень вкусно" in message for message in console.messages)


def test_delivery_creation_and_listing():
    console = ConsoleStub(["13", "1", "1", "Пётр", "1", "ул. Центральная, 10", "2", "13", "2", "0"])
    app = build_app(console)
    app.run()
    assert len(app.deliveries) == 1
    assert app.deliveries[0].status.value == "доставлен"
    assert any("ул. Центральная, 10" in message for message in console.messages)


def test_stop_list_is_available_from_console():
    console = ConsoleStub(["14", "0"])
    app = build_app(console)
    app.run()
    assert "Стоп-лист пуст. Все блюда обеспечены ингредиентами." in console.messages


def test_sales_report_after_payment():
    console = ConsoleStub(["4", "1", "1", "Иван", "8", "1", "8", "1", "8", "1", "9", "1", "2", "12", "0"])
    app = build_app(console)
    app.run()
    assert "Заказов оплачено: 1" in console.messages
    assert "Выручка: 5.00 руб." in console.messages


def test_cash_payment_prints_change():
    console = ConsoleStub(["4", "1", "1", "Иван", "8", "1", "8", "1", "8", "1", "9", "1", "1", "10", "0"])
    app = build_app(console)
    app.run()
    assert "Сдача: 5.00 руб." in console.messages
    assert app.cashier.transactions_count == 1


def test_payment_is_rejected_before_order_is_served():
    console = ConsoleStub(["4", "1", "1", "Иван", "9", "1", "0"])
    app = build_app(console)
    app.run()
    assert "Оплатить можно только заказ, который уже подан гостю." in console.messages
    assert not app.payments


def test_order_transition_rejects_unknown_order_number():
    console = ConsoleStub(["8", "42", "0"])
    app = build_app(console)
    app.run()
    assert "Заказов пока нет." in console.messages


def test_reservation_can_be_cancelled():
    console = ConsoleStub(["10", "Пётр", "2", "2026-11-25 19:00", "15", "3", "Пётр", "0"])
    app = build_app(console)
    app.run()
    assert app.reservations[0].is_cancelled
    assert "Бронирование отменено." in console.messages


def test_empty_reservation_list_is_reported():
    console = ConsoleStub(["15", "1", "0"])
    app = build_app(console)
    app.run()
    assert "Бронирований пока нет." in console.messages


def test_review_menu_rejects_unknown_action():
    console = ConsoleStub(["11", "9", "0"])
    build_app(console).run()
    assert "Неизвестный пункт меню." in console.messages


def test_review_rejects_invalid_dish_number():
    console = ConsoleStub(["11", "1", "99", "0"])
    build_app(console).run()
    assert "Блюда с таким номером нет." in console.messages


def test_delivery_menu_rejects_unknown_action():
    console = ConsoleStub(["13", "9", "0"])
    build_app(console).run()
    assert "Неизвестный пункт меню." in console.messages


def test_delivery_without_available_courier_is_rejected():
    console = ConsoleStub(["13", "1", "0"])
    app = build_app(console)
    app.couriers = []
    app.run()
    assert "Нет свободных курьеров." in console.messages


def test_stop_list_displays_missing_ingredients():
    console = ConsoleStub(["14", "0"])
    app = build_app(console)
    app.inventory = Inventory()
    app.run()
    assert any("Салат: не хватает Огурец: 100 г" in message for message in console.messages)


def test_invalid_payment_method_is_reported():
    console = ConsoleStub(["4", "1", "1", "Иван", "8", "1", "8", "1", "8", "1", "9", "1", "9", "0"])
    app = build_app(console)
    app.run()
    assert "Неизвестный способ оплаты." in console.messages


def test_order_can_be_advanced_only_until_served():
    console = ConsoleStub(["4", "1", "1", "Иван", "8", "1", "8", "1", "8", "1", "8", "1", "0"])
    app = build_app(console)
    app.run()
    assert "Для заказа №1 нет доступного перехода." in console.messages


def test_overlapping_reservation_is_rejected():
    console = ConsoleStub([
        "10", "Пётр", "2", "2026-11-25 19:00",
        "10", "Анна", "2", "2026-11-25 19:30", "0",
    ])
    app = build_app(console)
    app.run()
    assert len(app.reservations) == 1
    assert any("Стол №1 уже занят" in message for message in console.messages)
