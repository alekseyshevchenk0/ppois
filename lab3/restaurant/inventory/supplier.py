from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InvalidDataError
from restaurant.validation import require_non_empty, require_non_negative, require_positive


class Supplier:
    def __init__(self, name: str, phone: str, lead_time_days: int) -> None:
        require_non_empty(name, "supplier name")
        require_non_empty(phone, "supplier phone")
        require_non_negative(lead_time_days, "lead time")
        self.name = name
        self.phone = phone
        self.lead_time_days = lead_time_days
        self._price_list: dict[Ingredient, Decimal] = {}

    def set_price(self, ingredient: Ingredient, price_per_unit: Decimal) -> None:
        require_positive(price_per_unit, "price")
        self._price_list[ingredient] = price_per_unit

    def supplies(self, ingredient: Ingredient) -> bool:
        return ingredient in self._price_list

    def price_of(self, ingredient: Ingredient) -> Decimal:
        if not self.supplies(ingredient):
            raise InvalidDataError(f"Supplier '{self.name}' does not sell '{ingredient.name}'")
        return self._price_list[ingredient]

    def quote(self, ingredient: Ingredient, amount: float) -> Decimal:
        require_positive(amount, "amount")
        return self.price_of(ingredient) * Decimal(str(amount))

    def delivery_date(self, ordered_on: date) -> date:
        return ordered_on + timedelta(days=self.lead_time_days)
