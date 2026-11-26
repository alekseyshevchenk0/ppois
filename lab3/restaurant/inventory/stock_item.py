from __future__ import annotations

from datetime import date

from restaurant.catalog.ingredient import Ingredient
from restaurant.validation import require_positive

QUANTITY_EPSILON = 1e-9


class StockItem:
    def __init__(self, ingredient: Ingredient, quantity: float, received_on: date) -> None:
        require_positive(quantity, "количество в партии")
        self.ingredient = ingredient
        self.quantity = quantity
        self.received_on = received_on

    def expiry_date(self) -> date:
        return self.ingredient.expiry_date(self.received_on)

    def is_expired(self, today: date) -> bool:
        return today > self.expiry_date()

    def days_until_expiry(self, today: date) -> int:
        return (self.expiry_date() - today).days

    def is_empty(self) -> bool:
        return self.quantity <= QUANTITY_EPSILON

    def consume(self, amount: float) -> float:
        taken = min(amount, self.quantity)
        self.quantity -= taken
        return taken
