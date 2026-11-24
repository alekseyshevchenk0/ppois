from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Callable

from restaurant.analytics.dynamic_pricer import DynamicPricer
from restaurant.analytics.menu_recommender import MenuRecommender
from restaurant.exceptions import RestaurantError
from restaurant.guests.customer import Customer
from restaurant.hall.table import Table
from restaurant.inventory.inventory import Inventory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu
from restaurant.orders.order import Order
from restaurant.staff.waiter import Waiter


class RestaurantApp:
    def __init__(
        self,
        menu: Menu,
        inventory: Inventory,
        waiter: Waiter,
        table: Table,
        today: date | None = None,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self.menu = menu
        self.inventory = inventory
        self.waiter = waiter
        self.table = table
        self.today = today or date.today()
        self.input_fn, self.output_fn = input_fn, output_fn
        self.orders: list[Order] = []
        self._next_order_number = 1
        self.recommender = MenuRecommender(menu)
        self.pricer = self._create_pricer()

    @staticmethod
    def _create_pricer() -> DynamicPricer:
        return DynamicPricer(
            happy_hours=(time(14), time(16)),
            happy_discount=Decimal("10"),
            peak_hours=(time(18), time(21)),
            peak_surcharge=Decimal("10"),
            expiry_discount=Decimal("15"),
            expiry_threshold_days=2,
        )

    def run(self) -> None:
        self.output_fn("Cистема управления рестораном")
        while True:
            self._show_main_menu()
            choice = self._read_int("Выберите действие: ")
            if choice == 0:
                self.output_fn("Работа программы завершена")
                return
            self._dispatch(choice)

    def _show_main_menu(self) -> None:
        self.output_fn(
            "\nГЛАВНОЕ МЕНЮ\n"
            "1. Показать меню ресторана\n"
            "2. Показать доступные блюда\n"
            "3. Посмотреть остатки склада\n"
            "4. Создать заказ\n"
            "5. Посмотреть заказы\n"
            "6. Получить рекомендации\n"
            "7. Показать динамические цены\n"
            "0. Выход"
        )

    def _dispatch(self, choice: int) -> None:
        actions = {
            1: self._show_dishes,
            2: self._show_available_dishes,
            3: self._show_inventory,
            4: self._create_order,
            5: self._show_orders,
            6: self._show_recommendations,
            7: self._show_dynamic_prices,
        }
        action = actions.get(choice)
        if action is None:
            self.output_fn("Неизвестный пункт меню. Повторите ввод")
            return
        try:
            action()
        except RestaurantError as error:
            self.output_fn(f"Ошибка: {error}")

    def _show_dishes(self) -> None:
        dishes = self.menu.all_dishes()
        self._print_dishes(dishes)

    def _show_available_dishes(self) -> None:
        dishes = self.menu.available_dishes(self.inventory, self.today)
        self.output_fn("Доступные блюда:")
        self._print_dishes(dishes)

    def _show_inventory(self) -> None:
        report = self.inventory.stock_report(self.today)
        if not report:
            self.output_fn("Склад пока пуст")
            return
        for ingredient, quantity in sorted(report.items(), key=lambda item: item[0].name):
            self.output_fn(f"{ingredient.name}: {quantity:g} {ingredient.unit}")

    def _create_order(self) -> None:
        dishes = self.menu.available_dishes(self.inventory, self.today)
        if not dishes:
            self.output_fn("Сейчас нет доступных блюд для заказа")
            return
        self._print_dishes(dishes)
        index = self._read_int("Введите номер блюда: ")
        if not 1 <= index <= len(dishes):
            self.output_fn("Блюда с таким номером нет")
            return
        quantity = self._read_int("Введите количество порций: ")
        if quantity <= 0:
            self.output_fn("Количество порций должно быть положительным")
            return
        self._save_order(dishes[index - 1], quantity)

    def _save_order(self, dish: Dish, quantity: int) -> None:
        guest_name = self.input_fn("Введите имя гостя: ").strip()
        if not guest_name:
            self.output_fn("Имя гостя не должно быть пустым")
            return
        guest = Customer(guest_name, "+375330000000", date(2000, 1, 1), "guest@example.com")
        order = Order(self._next_order_number, self.table, self.waiter, guest, datetime.now())
        order.add_item(dish, quantity)
        self.orders.append(order)
        self._next_order_number += 1
        self.output_fn(f"Заказ №{order.number} создан. Сумма: {order.subtotal():.2f} руб.")

    def _show_orders(self) -> None:
        if not self.orders:
            self.output_fn("Заказов пока нет")
            return
        for order in self.orders:
            self.output_fn(
                f"Заказ №{order.number} | гость: {order.guest.name} | "
                f"статус: {order.status.value} | сумма: {order.subtotal():.2f} руб."
            )

    def _show_recommendations(self) -> None:
        guest_name = self.input_fn("Введите имя гостя: ").strip() or "Гость"
        guest = Customer(guest_name, "+3750000000", date(2000, 1, 1), "guest@example.com")
        dishes = self.recommender.recommend(guest, inventory=self.inventory, today=self.today)
        self.output_fn("Рекомендации для гостя:")
        self._print_dishes(dishes)

    def _show_dynamic_prices(self) -> None:
        dishes = self.menu.available_dishes(self.inventory, self.today)
        if not dishes:
            self.output_fn("Нет доступных блюд для расчёта цен")
            return
        moment = datetime.now()
        for dish in dishes:
            price = self.pricer.price_for(dish, moment, self.inventory)
            self.output_fn(f"{dish.name}: {price:.2f} руб.")

    def _print_dishes(self, dishes: list[Dish]) -> None:
        if not dishes:
            self.output_fn("Список пуст")
            return
        for index, dish in enumerate(dishes, start=1):
            status = "стоп-лист" if dish.is_stopped else "доступно"
            self.output_fn(f"{index}. {dish.name} — {dish.price:.2f} руб. ({status})")

    def _read_int(self, prompt: str) -> int:
        try:
            return int(self.input_fn(prompt))
        except ValueError:
            self.output_fn("Нужно ввести целое число")
            return -1
