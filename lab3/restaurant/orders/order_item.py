from __future__ import annotations

from decimal import Decimal

from restaurant.menu.dish import Dish
from restaurant.validation import require_positive


class OrderItem:
    def __init__(
        self,
        dish: Dish,
        quantity: int,
        note: str = "",
        unit_price: Decimal | None = None,
    ) -> None:
        require_positive(quantity, "количество")
        price = dish.price if unit_price is None else unit_price
        require_positive(price, "цена блюда")

        self.dish = dish
        self.quantity = quantity
        self.unit_price = price
        self.note = note

    def total(self) -> Decimal:
        return self.unit_price * self.quantity

    def change_quantity(self, quantity: int) -> None:
        require_positive(quantity, "количество")
        self.quantity = quantity

    def increase(self, extra: int) -> None:
        require_positive(extra, "дополнительное количество")
        self.quantity += extra

    def is_same_position(
        self,
        dish: Dish,
        note: str,
        unit_price: Decimal,
    ) -> bool:
        return (
            self.dish is dish
            and self.note == note
            and self.unit_price == unit_price
        )

    def cooking_minutes(self) -> int:
        return self.dish.recipe.cooking_time_for(self.quantity)
