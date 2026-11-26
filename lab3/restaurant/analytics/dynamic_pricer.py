from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from restaurant.exceptions import InvalidDataError
from restaurant.inventory.inventory import Inventory
from restaurant.menu.dish import Dish
from restaurant.money import apply_percent


class DynamicPricer:
    def __init__(
        self,
        happy_hours: tuple[time, time] | None = None,
        happy_discount: Decimal = Decimal(0),
        peak_hours: tuple[time, time] | None = None,
        peak_surcharge: Decimal = Decimal(0),
        expiry_discount: Decimal = Decimal(0),
        expiry_threshold_days: int = 2,
    ) -> None:
        percentages = (happy_discount, peak_surcharge, expiry_discount)
        if any(value < 0 or value > 100 for value in percentages) or expiry_threshold_days < 0:
            raise InvalidDataError("Проценты должны быть от 0 до 100, срок — неотрицательным")
        self.happy_hours = happy_hours
        self.happy_discount = happy_discount
        self.peak_hours = peak_hours
        self.peak_surcharge = peak_surcharge
        self.expiry_discount = expiry_discount
        self.expiry_threshold_days = expiry_threshold_days

    def price_for(self, dish: Dish, moment: datetime, inventory: Inventory | None = None) -> Decimal:
        adjustment = self._time_adjustment(moment.time())
        if self._has_expiring_ingredients(dish, inventory, moment.date()):
            adjustment -= self.expiry_discount
        price = apply_percent(dish.price, adjustment)
        if price <= 0:
            raise InvalidDataError("Динамическая цена должна быть положительной")
        return price

    def _time_adjustment(self, current: time) -> Decimal:
        if self._contains(self.happy_hours, current):
            return -self.happy_discount
        if self._contains(self.peak_hours, current):
            return self.peak_surcharge
        return Decimal(0)

    def _has_expiring_ingredients(self, dish: Dish, inventory: Inventory | None, today: date) -> bool:
        if inventory is None or self.expiry_discount == 0:
            return False
        return any(
            (days := inventory.earliest_expiry_days(ingredient, today)) is not None
            and days <= self.expiry_threshold_days
            for ingredient in dish.recipe.ingredients()
        )

    @staticmethod
    def _contains(period: tuple[time, time] | None, current: time) -> bool:
        if period is None:
            return False
        start, end = period
        if start <= end:
            return start <= current <= end
        return current >= start or current <= end
