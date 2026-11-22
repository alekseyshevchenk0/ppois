from __future__ import annotations

from decimal import Decimal

from restaurant.menu.dish import Dish
from restaurant.validation import require_positive


class OrderItem:
    def __init__(self, dish: Dish, quantity: int, note: str = "") -> None:
        require_positive(quantity, "quantity")
        self.dish = dish
        self.quantity = quantity
        self.unit_price = dish.price
        self.note = note

    def total(self) -> Decimal:
        return self.unit_price * self.quantity

    def change_quantity(self, quantity: int) -> None:
        require_positive(quantity, "quantity")
        self.quantity = quantity

    def increase(self, extra: int) -> None:
        require_positive(extra, "extra quantity")
        self.quantity += extra

    def is_same_position(self, dish: Dish, note: str) -> bool:
        return self.dish is dish and self.note == note

    def cooking_minutes(self) -> int:
        return self.dish.recipe.cooking_time_for(self.quantity)
