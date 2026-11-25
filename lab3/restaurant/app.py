from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Callable

from restaurant.analytics.dynamic_pricer import DynamicPricer
from restaurant.analytics.menu_recommender import MenuRecommender
from restaurant.analytics.review import Review
from restaurant.analytics.sales_report import SalesReport
from restaurant.catalog.ingredient import Ingredient
from restaurant.delivery.courier import Courier
from restaurant.delivery.delivery_order import DeliveryOrder
from restaurant.exceptions import RestaurantError
from restaurant.guests.customer import Customer
from restaurant.hall.reservation import Reservation
from restaurant.hall.reservation_book import ReservationBook
from restaurant.hall.table import Table
from restaurant.inventory.inventory import Inventory
from restaurant.kitchen.kitchen import Kitchen
from restaurant.menu.category import MenuCategory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu
from restaurant.menu.recipe import Recipe
from restaurant.orders.bill import Bill
from restaurant.orders.order import Order, OrderStatus
from restaurant.orders.payment import Payment, PaymentMethod
from restaurant.staff.cashier import Cashier
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
        cashier: Cashier | None = None,
        couriers: list[Courier] | None = None,
        kitchen: Kitchen | None = None,
    ) -> None:
        self._initialize_dependencies(menu, inventory, waiter, table, today, input_fn, output_fn)
        self._initialize_records(cashier, couriers, kitchen)
        self.reservation_book = ReservationBook()
        self.recommender = MenuRecommender(menu)
        self.pricer = self._create_pricer()

    def _initialize_dependencies(
        self, menu: Menu, inventory: Inventory, waiter: Waiter, table: Table, today: date | None,
        input_fn: Callable[[str], str], output_fn: Callable[[str], None],
    ) -> None:
        self.menu, self.inventory = menu, inventory
        self.waiter, self.table = waiter, table
        self.today = today or date.today()
        self.input_fn, self.output_fn = input_fn, output_fn

    def _initialize_records(
        self, cashier: Cashier | None, couriers: list[Courier] | None, kitchen: Kitchen | None
    ) -> None:
        self.cashier, self.couriers, self.kitchen = cashier, couriers or [], kitchen
        self.orders, self.reservations, self.payments = [], [], []
        self.reviews, self.deliveries = [], []
        self._next_order_number, self._next_delivery_number = 1, 1

    @staticmethod
    def _create_pricer() -> DynamicPricer:
        return DynamicPricer(
            happy_hours=(time(14), time(16)), happy_discount=Decimal("10"),
            peak_hours=(time(18), time(21)), peak_surcharge=Decimal("10"),
            expiry_discount=Decimal("15"), expiry_threshold_days=2,
        )

    def run(self) -> None:
        self.output_fn("Добро пожаловать в систему управления рестораном!")
        while True:
            self._show_main_menu()
            choice = self._read_int("Выберите действие: ")
            if choice == 0:
                self.output_fn("Работа программы завершена.")
                return
            self._dispatch(choice)

    def _show_main_menu(self) -> None:
        self.output_fn(
            "\nГЛАВНОЕ МЕНЮ\n"
            "1. Показать меню ресторана\n2. Показать доступные блюда\n"
            "3. Посмотреть остатки склада\n4. Создать заказ\n5. Посмотреть заказы\n"
            "6. Получить рекомендации\n7. Показать динамические цены\n"
            "8. Управление приготовлением и подачей заказа\n9. Оплатить заказ\n10. Создать бронирование\n"
            "11. Отзывы о блюдах\n12. Отчёт о продажах\n13. Управление доставкой\n"
            "14. Показать стоп-лист\n15. Управление бронированиями\n"
            "16. Добавить блюдо\n17. Изменить цену блюда\n18. Удалить блюдо\n"
            "19. Пополнить склад\n0. Выход"
        )

    def _dispatch(self, choice: int) -> None:
        actions = {
            1: self._show_dishes, 2: self._show_available_dishes, 3: self._show_inventory,
            4: self._create_order, 5: self._show_orders, 6: self._show_recommendations,
            7: self._show_dynamic_prices, 8: self._advance_order, 9: self._pay_order,
            10: self._create_reservation, 11: self._manage_reviews, 12: self._show_sales_report,
            13: self._manage_delivery, 14: self._show_stop_list, 15: self._manage_reservations,
            16: self._add_dish, 17: self._edit_dish, 18: self._delete_dish,
            19: self._replenish_inventory,
        }
        action = actions.get(choice)
        if action is None:
            self.output_fn("Неизвестный пункт меню. Повторите ввод.")
            return
        try:
            action()
        except (RestaurantError, ValueError) as error:
            self.output_fn(f"Ошибка: {error}")

    def _add_dish(self) -> None:
        details = self._read_dish_details()
        if details is None:
            return
        name, category_name, price, minutes = details
        requirements = self._read_recipe_requirements()
        if not requirements:
            self.output_fn("У блюда должен быть хотя бы один ингредиент.")
            return
        step = self._read_recipe_step()
        if step is None:
            return
        self._save_new_dish(name, category_name, price, minutes, requirements, step)

    def _read_dish_details(self) -> tuple[str, str, Decimal, int] | None:
        name = self.input_fn("Название нового блюда: ").strip()
        if not name or self.menu.find_dish(name) is not None:
            self.output_fn("Название пустое или такое блюдо уже существует.")
            return None
        category_name = self.input_fn("Категория блюда: ").strip()
        if not category_name:
            self.output_fn("Название категории не должно быть пустым.")
            return None
        price = self._read_money("Цена блюда (руб.): ")
        minutes = self._read_int("Время приготовления (мин.): ")
        if price <= 0 or minutes <= 0:
            self.output_fn("Цена и время приготовления должны быть положительными.")
            return None
        return name, category_name, price, minutes

    def _read_recipe_step(self) -> str | None:
        step = self.input_fn("Шаг приготовления: ").strip()
        if not step:
            self.output_fn("Шаг приготовления не должен быть пустым.")
            return None
        return step

    def _save_new_dish(
        self, name: str, category_name: str, price: Decimal, minutes: int,
        requirements: dict[Ingredient, float], step: str,
    ) -> None:
        category = self._get_or_create_category(category_name)
        recipe = Recipe([step], minutes, station="универсальный цех")
        for ingredient, amount in requirements.items():
            recipe.add_requirement(ingredient, amount)
        self.menu.add_dish(category.name, Dish(name, price, recipe))
        self.output_fn(f"Блюдо «{name}» добавлено в категорию «{category.name}».")

    def _get_or_create_category(self, name: str) -> MenuCategory:
        category = next((item for item in self.menu.categories if item.name == name), None)
        if category is None:
            category = MenuCategory(name)
            self.menu.add_category(category)
        return category

    def _read_recipe_requirements(self) -> dict[Ingredient, float]:
        ingredients = sorted(self.inventory.stock_report(self.today), key=lambda item: item.name)
        if not ingredients:
            self.output_fn("На складе нет ингредиентов. Добавить блюдо невозможно.")
            return {}
        self._show_stock_ingredients(ingredients)
        return self._collect_recipe_requirements(ingredients)

    def _show_stock_ingredients(self, ingredients: list[Ingredient]) -> None:
        self.output_fn("Ингредиенты со склада:")
        for index, ingredient in enumerate(ingredients, 1):
            quantity = self.inventory.total_of(ingredient, self.today)
            self.output_fn(f"{index}. {ingredient.name} — {quantity:g} {ingredient.unit}")

    def _collect_recipe_requirements(
        self, ingredients: list[Ingredient],
    ) -> dict[Ingredient, float]:
        requirements = {}
        while True:
            choice = self._read_int("Номер ингредиента (0 — завершить): ")
            if choice == 0:
                return requirements
            self._add_selected_ingredient(choice, ingredients, requirements)

    def _add_selected_ingredient(
        self, choice: int, ingredients: list[Ingredient], requirements: dict[Ingredient, float],
    ) -> None:
        if not 1 <= choice <= len(ingredients):
            self.output_fn("Ингредиента с таким номером нет.")
            return
        amount = self._read_positive_float("Количество на одну порцию: ")
        if amount > 0:
            requirements[ingredients[choice - 1]] = amount

    def _edit_dish(self) -> None:
        dishes = self.menu.all_dishes()
        self._print_dishes(dishes)
        if not dishes:
            return
        choice = self._read_int("Номер блюда для изменения цены: ")
        if not 1 <= choice <= len(dishes):
            self.output_fn("Блюда с таким номером нет.")
            return
        dish = dishes[choice - 1]
        new_price = self._read_money("Новая цена (руб.): ")
        if new_price <= 0:
            self.output_fn("Цена должна быть положительной.")
            return
        dish.price = new_price
        self.output_fn(f"Цена блюда «{dish.name}» изменена на {new_price:.2f} руб.")

    def _delete_dish(self) -> None:
        dishes = self.menu.all_dishes()
        self._print_dishes(dishes)
        if not dishes:
            return
        choice = self._read_int("Номер блюда для удаления: ")
        if not 1 <= choice <= len(dishes):
            self.output_fn("Блюда с таким номером нет.")
            return
        dish = dishes[choice - 1]
        self.menu.remove_dish(dish.name)
        self.output_fn(f"Блюдо «{dish.name}» удалено из меню.")

    def _read_positive_float(self, prompt: str) -> float:
        try:
            value = float(self.input_fn(prompt).replace(",", "."))
        except ValueError:
            self.output_fn("Нужно ввести число.")
            return 0.0
        if value <= 0:
            self.output_fn("Количество должно быть положительным.")
            return 0.0
        return value

    def _show_dishes(self) -> None:
        self._print_dishes(self.menu.all_dishes())

    def _show_available_dishes(self) -> None:
        self.output_fn("Доступные блюда:")
        self._print_dishes(self.menu.available_dishes(self.inventory, self.today))

    def _show_inventory(self) -> None:
        report = self.inventory.stock_report(self.today)
        if not report:
            self.output_fn("Склад пока пуст.")
            return
        for ingredient, quantity in sorted(report.items(), key=lambda item: item[0].name):
            self.output_fn(f"{ingredient.name}: {quantity:g} {ingredient.unit}")

    def _replenish_inventory(self) -> None:
        ingredients = {
            ingredient
            for dish in self.menu.all_dishes()
            for ingredient in dish.recipe.requirements_for(1)
        }
        ingredients = sorted(ingredients, key=lambda item: item.name)

        if not ingredients:
            self.output_fn("Нет известных ингредиентов.")
            return

        self.output_fn("Ингредиенты:")
        for index, ingredient in enumerate(ingredients, 1):
            quantity = self.inventory.total_of(ingredient, self.today)
            self.output_fn(
                f"{index}. {ingredient.name} — "
                f"{quantity:g} {ingredient.unit}"
            )

        choice = self._read_int("Выберите ингредиент: ")
        if not 1 <= choice <= len(ingredients):
            self.output_fn("Ингредиента с таким номером нет.")
            return

        ingredient = ingredients[choice - 1]
        quantity = self._read_positive_float("Количество поступления: ")
        if quantity <= 0:
            return

        received_on_text = self.input_fn(
            f"Дата поступления (ГГГГ-ММ-ДД, Enter — {self.today}): "
        ).strip()

        received_on = (
            date.fromisoformat(received_on_text)
            if received_on_text
            else self.today
        )

        self.inventory.receive(ingredient, quantity, received_on)

        self.output_fn(
            f"На склад поступило {quantity:g} {ingredient.unit} "
            f"ингредиента «{ingredient.name}»."
        )

    def _create_order(self) -> None:
        dishes = self.menu.available_dishes(self.inventory, self.today)
        if not dishes:
            self.output_fn("Сейчас нет доступных блюд для заказа.")
            return
        self._print_dishes(dishes)
        index = self._read_int("Введите номер блюда: ")
        if not 1 <= index <= len(dishes):
            self.output_fn("Блюда с таким номером нет.")
            return
        quantity = self._read_int("Введите количество порций: ")
        if quantity <= 0:
            self.output_fn("Количество порций должно быть положительным.")
            return
        self._save_order(dishes[index - 1], quantity)

    def _save_order(self, dish: Dish, quantity: int) -> None:
        guest = self._read_guest()
        if guest is None:
            return

        moment = datetime.now()
        dynamic_price = self.pricer.price_for(
            dish,
            moment,
            self.inventory,
        )

        order = Order(
            self._next_order_number,
            self.table,
            self.waiter,
            guest,
            moment,
        )
        order.add_item(
            dish,
            quantity,
            unit_price=dynamic_price,
        )

        self.orders.append(order)
        self._next_order_number += 1

        self.output_fn(
            f"Заказ №{order.number} создан. "
            f"Сумма: {order.subtotal():.2f} руб."
        )

    def _show_orders(self) -> None:
        if not self.orders:
            self.output_fn("Заказов пока нет.")
            return
        for order in self.orders:
            self._print_order(order)

    def _print_order(self, order: Order) -> None:
        self.output_fn(
            f"Заказ №{order.number} | гость: {order.guest.name} | "
            f"статус: {order.status.value} | сумма: {order.subtotal():.2f} руб."
        )

    def _show_recommendations(self) -> None:
        dishes = self.recommender.recommend(
            inventory=self.inventory,
            today=self.today,
        )
        self.output_fn("Рекомендации блюд:")
        self._print_dishes(dishes)

    def _show_dynamic_prices(self) -> None:
        dishes = self.menu.available_dishes(self.inventory, self.today)
        if not dishes:
            self.output_fn("Нет доступных блюд для расчёта цен.")
            return
        for dish in dishes:
            price = self.pricer.price_for(dish, datetime.now(), self.inventory)
            self.output_fn(f"{dish.name}: {price:.2f} руб.")

    def _advance_order(self) -> None:
        order = self._select_order()
        if order is None:
            return
        transitions = {
            OrderStatus.NEW: (lambda: self._send_order_to_kitchen(order), "Заказ отправлен на кухню."),
            OrderStatus.IN_PROGRESS: (lambda: self._finish_kitchen_order(order), "Приготовление завершено."),
            OrderStatus.READY: (order.mark_served, "Заказ подан гостю."),
        }
        transition = transitions.get(order.status)
        self._apply_order_transition(order, transition)

    def _send_order_to_kitchen(self, order: Order) -> None:
        if self.kitchen is not None:
            self.kitchen.accept_order(order, datetime.now())
            return
        order.validate_for_kitchen()
        self.inventory.consume_all(self._order_requirements(order), self.today)
        order.send_to_kitchen()

    def _finish_kitchen_order(self, order: Order) -> None:
        if self.kitchen is None:
            order.mark_ready()
            return
        for ticket in self.kitchen.tickets_of(order.number):
            if not ticket.is_done:
                self.kitchen.finish_ticket(ticket, datetime.now())

    def _order_requirements(self, order: Order) -> dict[Ingredient, float]:
        requirements = {}
        for item in order.items:
            for ingredient, amount in item.dish.recipe.requirements_for(item.quantity).items():
                requirements[ingredient] = requirements.get(ingredient, 0) + amount
        return requirements

    def _apply_order_transition(self, order: Order, transition: tuple[Callable[[], None], str] | None) -> None:
        if transition is None:
            self.output_fn(f"Для заказа №{order.number} нет доступного перехода.")
            return
        transition[0]()
        self.output_fn(transition[1])

    def _pay_order(self) -> None:
        order = self._select_order()
        if order is None:
            return
        bill = Bill(order)
        self._process_payment(bill)

    def _process_payment(self, bill: Bill) -> None:
        if bill.order.status is not OrderStatus.SERVED:
            self.output_fn("Оплатить можно только заказ, который уже подан гостю.")
            return
        method = self._read_payment_method()
        if method is None:
            return
        self._complete_payment(bill, method)

    def _complete_payment(self, bill: Bill, method: PaymentMethod) -> None:
        due = bill.total_with_tip()
        tendered = self._read_money("Внесённая сумма: ") if method is PaymentMethod.CASH else due
        payment_time = datetime.combine(self.today, datetime.now().time())
        payment = Payment(bill, method, tendered, payment_time)
        payment.process(self.cashier)
        self.payments.append(payment)
        self._print_receipt(bill, payment)

    def _print_receipt(self, bill: Bill, payment: Payment) -> None:
        self.output_fn("ЧЕК")
        for line in bill.receipt_lines():
            self.output_fn(line)
        self.output_fn(f"Способ оплаты: {payment.method.value}")
        if payment.change:
            self.output_fn(f"Сдача: {payment.change:.2f} руб.")

    def _create_reservation(self) -> None:
        guest = self._read_guest()
        if guest is None:
            return
        guests_count = self._read_int("Количество гостей: ")
        start = datetime.fromisoformat(self.input_fn("Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ): "))
        reservation = self.reservation_book.book(guest, self.table, start, guests_count)
        self.reservations.append(reservation)
        self.output_fn(f"Бронирование создано. Стол №{self.table.number}.")

    def _manage_reservations(self) -> None:
        self.output_fn("1. Показать бронирования\n2. Отметить прибытие гостя\n3. Отменить бронирование")
        choice = self._read_int("Выберите действие: ")
        if choice == 1:
            self._show_reservations()
        elif choice in (2, 3):
            self._update_reservation(choice)
        else:
            self.output_fn("Неизвестный пункт меню.")

    def _update_reservation(self, choice: int) -> None:
        reservation = self._select_reservation()
        if reservation is None:
            return
        reservation.mark_arrived() if choice == 2 else self.reservation_book.cancel(reservation)
        message = "Прибытие гостя отмечено." if choice == 2 else "Бронирование отменено."
        self.output_fn(message)

    def _select_reservation(self) -> Reservation | None:
        if not self.reservations:
            self.output_fn("Бронирований пока нет.")
            return None
        self._show_reservations()
        guest_name = self.input_fn("Введите имя гостя: ").strip()
        reservation = next((item for item in self.reservations if item.guest.name == guest_name), None)
        if reservation is None:
            self.output_fn("Бронирование для этого гостя не найдено.")
        return reservation

    def _show_reservations(self) -> None:
        if not self.reservations:
            self.output_fn("Бронирований пока нет.")
            return
        for reservation in self.reservations:
            self._print_reservation(reservation)

    def _print_reservation(self, reservation: Reservation) -> None:
        status = "отменено" if reservation.is_cancelled else "активно"
        self.output_fn(
            f"{reservation.start:%d.%m.%Y %H:%M} | {reservation.guest.name} | "
            f"стол №{reservation.table.number} | гостей: {reservation.guests_count} | {status}"
        )

    def _manage_reviews(self) -> None:
        self.output_fn("1. Оставить отзыв\n2. Показать одобренные отзывы")
        choice = self._read_int("Выберите действие: ")
        if choice == 1:
            self._create_review()
        elif choice == 2:
            self._show_reviews()
        else:
            self.output_fn("Неизвестный пункт меню.")

    def _create_review(self) -> None:
        dishes = self.menu.all_dishes()
        self._print_dishes(dishes)
        index = self._read_int("Номер блюда: ")
        if not 1 <= index <= len(dishes):
            self.output_fn("Блюда с таким номером нет.")
            return
        guest = self._read_guest()
        if guest is None:
            return
        rating = self._read_int("Оценка от 1 до 5: ")
        review = Review(guest, dishes[index - 1], rating, self.input_fn("Комментарий: "), self.today)
        review.approve()
        self.reviews.append(review)
        self.output_fn("Спасибо! Отзыв опубликован.")

    def _show_reviews(self) -> None:
        visible = [review for review in self.reviews if review.is_visible()]
        if not visible:
            self.output_fn("Опубликованных отзывов пока нет.")
            return
        for review in visible:
            self.output_fn(f"{review.dish.name} | {review.customer.name} | {review.rating}/5 | {review.comment}")

    def _show_sales_report(self) -> None:
        report = SalesReport(self.payments, self.today, self.today)
        self.output_fn(f"Заказов оплачено: {report.orders_count()}")
        self.output_fn(f"Выручка: {report.total_revenue():.2f} руб.")
        self.output_fn(f"Средний чек: {report.average_check():.2f} руб.")
        self._print_popular_dishes(report)

    def _print_popular_dishes(self, report: SalesReport) -> None:
        for name, quantity in report.popular_dishes():
            self.output_fn(f"{name}: {quantity} порц.")

    def _manage_delivery(self) -> None:
        self.output_fn("1. Создать и выполнить доставку\n2. Показать доставки")
        choice = self._read_int("Выберите действие: ")
        if choice == 1:
            self._create_delivery()
        elif choice == 2:
            self._show_deliveries()
        else:
            self.output_fn("Неизвестный пункт меню.")

    def _create_delivery(self) -> None:
        courier = self._select_courier()
        if courier is None:
            return
        guest = self._read_guest()
        if guest is None:
            return
        dish = self._select_dish()
        if dish is None:
            return
        delivery = self._build_delivery(guest, dish)
        delivery.assign_courier(courier)
        delivery.pick_up()
        delivery.deliver()
        self.deliveries.append(delivery)
        self.output_fn(f"Доставка №{delivery.number} завершена. Сумма: {delivery.total():.2f} руб.")

    def _build_delivery(self, guest: Customer, dish: Dish) -> DeliveryOrder:
        address = self.input_fn("Адрес доставки: ").strip()
        quantity = self._read_int("Количество порций: ")
        delivery = DeliveryOrder(
            self._next_delivery_number, guest, address, datetime.now(), Decimal("5.00")
        )
        delivery.add_item(dish, quantity)
        self._next_delivery_number += 1
        return delivery

    def _show_deliveries(self) -> None:
        if not self.deliveries:
            self.output_fn("Доставок пока нет.")
            return
        for delivery in self.deliveries:
            self.output_fn(
                f"Доставка №{delivery.number} | {delivery.customer.name} | "
                f"{delivery.address} | {delivery.status.value} | {delivery.total():.2f} руб."
            )

    def _show_stop_list(self) -> None:
        stop_list = self.menu.stop_list(self.inventory, self.today)
        if not stop_list:
            self.output_fn("Стоп-лист пуст. Все блюда обеспечены ингредиентами.")
            return
        for dish_name, missing in stop_list.items():
            details = ", ".join(f"{item.name}: {amount:g} {item.unit}" for item, amount in missing.items())
            self.output_fn(f"{dish_name}: не хватает {details}")

    def _select_order(self) -> Order | None:
        if not self.orders:
            self.output_fn("Заказов пока нет.")
            return None
        self._show_orders()
        number = self._read_int("Введите номер заказа: ")
        order = next((item for item in self.orders if item.number == number), None)
        if order is None:
            self.output_fn("Заказ с таким номером не найден.")
        return order

    def _select_dish(self) -> Dish | None:
        dishes = self.menu.available_dishes(self.inventory, self.today)
        self._print_dishes(dishes)
        index = self._read_int("Номер блюда: ")
        if not 1 <= index <= len(dishes):
            self.output_fn("Блюда с таким номером нет.")
            return None
        return dishes[index - 1]

    def _select_courier(self) -> Courier | None:
        available = [courier for courier in self.couriers if courier.is_available()]
        if not available:
            self.output_fn("Нет свободных курьеров.")
            return None
        for index, courier in enumerate(available, 1):
            self.output_fn(f"{index}. {courier.name} ({courier.transport})")
        choice = self._read_int("Выберите курьера: ")
        if not 1 <= choice <= len(available):
            self.output_fn("Курьер с таким номером не найден.")
            return None
        return available[choice - 1]

    def _read_guest(self, allow_empty: bool = False) -> Customer | None:
        name = self.input_fn("Введите имя гостя: ").strip()
        if not name and not allow_empty:
            self.output_fn("Имя гостя не должно быть пустым.")
            return None
        return Customer(name or "Гость", "+70000000000", date(2000, 1, 1), "guest@example.com")

    def _read_payment_method(self) -> PaymentMethod | None:
        self.output_fn("1. Наличные\n2. Банковская карта")
        choice = self._read_int("Способ оплаты: ")
        methods = {1: PaymentMethod.CASH, 2: PaymentMethod.CARD}
        method = methods.get(choice)
        if method is None:
            self.output_fn("Неизвестный способ оплаты.")
        return method

    def _read_money(self, prompt: str) -> Decimal:
        return Decimal(self.input_fn(prompt).replace(",", "."))

    def _print_dishes(self, dishes: list[Dish]) -> None:
        if not dishes:
            self.output_fn("Список пуст.")
            return
        for index, dish in enumerate(dishes, start=1):
            status = "стоп-лист" if dish.is_stopped else "доступно"
            self.output_fn(f"{index}. {dish.name} — {dish.price:.2f} руб. ({status})")

    def _read_int(self, prompt: str) -> int:
        try:
            return int(self.input_fn(prompt))
        except ValueError:
            self.output_fn("Нужно ввести целое число.")
            return -1
