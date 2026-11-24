from datetime import datetime, time, timedelta
from decimal import Decimal

import pytest

from restaurant.analytics.dynamic_pricer import DynamicPricer
from restaurant.analytics.menu_recommender import MenuRecommender
from restaurant.analytics.review import Review, ReviewStatus
from restaurant.analytics.sales_report import SalesReport
from restaurant.delivery.courier import Courier
from restaurant.delivery.delivery_order import DeliveryOrder, DeliveryStatus
from restaurant.exceptions import EmployeeNotAvailableError, InvalidDataError
from restaurant.inventory.inventory import Inventory
from restaurant.inventory.waste_log import WasteLog
from restaurant.menu.category import MenuCategory
from restaurant.menu.menu import Menu
from restaurant.orders.bill import Bill
from restaurant.orders.payment import Payment, PaymentMethod
from tests.constants import ADULT_BIRTH, HIRED_ON, HOURLY_RATE, NOW, PHONE, TODAY


def test_review_moderation(adult_guest, pancakes):
    review = Review(adult_guest, pancakes, 5, " Отличное блюдо ", TODAY)
    assert review.comment == "Отличное блюдо"
    assert review.status is ReviewStatus.PENDING
    assert not review.is_visible()
    review.approve()
    assert review.is_visible()
    with pytest.raises(InvalidDataError):
        review.reject()


def test_review_rejects_invalid_rating(adult_guest, pancakes):
    with pytest.raises(InvalidDataError):
        Review(adult_guest, pancakes, 6, "Плохо", TODAY)


def test_sales_report_counts_completed_payments(order, pancakes):
    order.add_item(pancakes, 2)
    order.send_to_kitchen()
    order.mark_ready()
    order.mark_served()
    bill = Bill(order)
    payment = Payment(bill, PaymentMethod.CARD, Decimal("15.00"), NOW)
    payment.process()
    report = SalesReport([payment], TODAY, TODAY)
    assert report.orders_count() == 1
    assert report.total_revenue() == Decimal("15.00")
    assert report.average_check() == Decimal("15.00")
    assert report.popular_dishes() == [("Pancakes", 2)]
    assert report.revenue_by_day() == {TODAY: Decimal("15.00")}


def test_sales_report_ignores_uncompleted_payments(order):
    report = SalesReport([], TODAY, TODAY)
    assert report.orders_count() == 0
    assert report.average_check() == 0
    assert report.popular_dishes() == []


def test_sales_report_rejects_invalid_period():
    with pytest.raises(InvalidDataError):
        SalesReport([], TODAY + timedelta(days=1), TODAY)


def test_menu_recommender_respects_guest_profile(adult_guest, pancakes, salad):
    menu = Menu("Основное меню")
    category = MenuCategory("Основные блюда")
    category.add_dish(pancakes)
    category.add_dish(salad)
    menu.add_category(category)
    adult_guest.profile.record_order(salad.name, 3)
    recommender = MenuRecommender(menu)
    assert recommender.recommend(adult_guest) == [salad, pancakes]


def test_menu_recommender_filters_allergens(gold_guest, pancakes, salad):
    menu = Menu("Основное меню")
    category = MenuCategory("Основные блюда")
    category.add_dish(pancakes)
    category.add_dish(salad)
    menu.add_category(category)
    gold_guest.profile.add_allergen(next(iter(pancakes.allergens())))
    assert MenuRecommender(menu).recommend(gold_guest) == [salad]


def test_menu_recommender_validates_limit(adult_guest):
    with pytest.raises(InvalidDataError):
        MenuRecommender(Menu("Меню")).recommend(adult_guest, 0)


def test_dynamic_pricer_happy_hour_and_peak(pancakes):
    pricer = DynamicPricer(
        happy_hours=(time(15), time(17)),
        happy_discount=Decimal(20),
        peak_hours=(time(18), time(21)),
        peak_surcharge=Decimal(10),
    )
    assert pricer.price_for(pancakes, datetime(2026, 11, 23, 16)) == Decimal("6.00")
    assert pricer.price_for(pancakes, datetime(2026, 11, 23, 19)) == Decimal("8.25")
    assert pricer.price_for(pancakes, datetime(2026, 11, 23, 12)) == pancakes.price


def test_dynamic_pricer_expiring_ingredients(pancakes, flour, milk):
    inventory = Inventory()
    inventory.receive(flour, 5000, TODAY)
    inventory.receive(milk, 5000, TODAY - timedelta(days=5))
    pricer = DynamicPricer(expiry_discount=Decimal(15), expiry_threshold_days=2)
    assert pricer.price_for(pancakes, datetime.combine(TODAY, time(12)), inventory) == Decimal("6.38")


def test_dynamic_pricer_validates_percentages():
    with pytest.raises(InvalidDataError):
        DynamicPricer(happy_discount=Decimal(101))


def test_courier_delivery_lifecycle(adult_guest, pancakes):
    courier = Courier("Курьер", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, "велосипед")
    delivery = DeliveryOrder(10, adult_guest, "ул. Ленина, 1", NOW, Decimal("3.00"))
    delivery.add_item(pancakes, 2)
    delivery.assign_courier(courier)
    assert delivery.status is DeliveryStatus.ASSIGNED
    assert not courier.is_available()
    assert delivery.total() == Decimal("18.00")
    delivery.pick_up()
    delivery.deliver()
    assert delivery.status is DeliveryStatus.DELIVERED
    assert courier.is_available()
    assert courier.completed_deliveries == 1


def test_courier_cannot_take_two_deliveries(adult_guest, pancakes):
    courier = Courier("Курьер", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, "автомобиль")
    first = DeliveryOrder(1, adult_guest, "Адрес 1", NOW)
    second = DeliveryOrder(2, adult_guest, "Адрес 2", NOW)
    first.add_item(pancakes)
    second.add_item(pancakes)
    first.assign_courier(courier)
    with pytest.raises(EmployeeNotAvailableError):
        second.assign_courier(courier)


def test_delivery_cancel_releases_courier(adult_guest, pancakes):
    courier = Courier("Курьер", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, "пешком")
    delivery = DeliveryOrder(3, adult_guest, "Адрес", NOW)
    delivery.add_item(pancakes)
    delivery.assign_courier(courier)
    delivery.cancel()
    assert courier.is_available()
    assert delivery.status is DeliveryStatus.CANCELLED


def test_delivery_requires_items_and_valid_transitions(adult_guest, pancakes):
    courier = Courier("Курьер", PHONE, ADULT_BIRTH, HOURLY_RATE, HIRED_ON, "пешком")
    delivery = DeliveryOrder(4, adult_guest, "Адрес", NOW)
    with pytest.raises(InvalidDataError):
        delivery.assign_courier(courier)
    delivery.add_item(pancakes)
    with pytest.raises(InvalidDataError):
        delivery.deliver()


def test_waste_log_records_and_aggregates(flour, milk):
    log = WasteLog()
    log.record(flour, 100, TODAY, "истёк срок годности")
    log.record(milk, 50, TODAY, "повреждена упаковка")
    log.record(flour, 25, TODAY, "истёк срок годности")
    assert log.total_quantity() == 175
    assert log.total_quantity(flour) == 125
    assert log.quantity_by_reason() == {"истёк срок годности": 125, "повреждена упаковка": 50}
    entries = log.entries
    entries.clear()
    assert len(log.entries) == 3


def test_waste_log_validates_record(flour):
    with pytest.raises(InvalidDataError):
        WasteLog().record(flour, 0, TODAY, "порча")
