from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from restaurant.catalog.allergen import Allergen
from restaurant.menu.dish import Dish
from restaurant.validation import require_positive


class GuestProfile:
    def __init__(
        self,
        forbidden_allergens: Iterable[Allergen] = (),
        is_vegetarian: bool = False,
        max_dish_price: Decimal | None = None,
    ) -> None:
        self.forbidden_allergens = set(forbidden_allergens)
        self.is_vegetarian = is_vegetarian
        self.max_dish_price = max_dish_price
        self._order_counts: dict[str, int] = {}

    def add_allergen(self, allergen: Allergen) -> None:
        self.forbidden_allergens.add(allergen)

    def remove_allergen(self, allergen: Allergen) -> None:
        self.forbidden_allergens.discard(allergen)

    def accepts(self, dish: Dish) -> bool:
        if dish.allergens() & self.forbidden_allergens:
            return False
        if self.is_vegetarian and not dish.is_vegetarian():
            return False
        return self.max_dish_price is None or dish.price <= self.max_dish_price

    def record_order(self, dish_name: str, quantity: int = 1) -> None:
        require_positive(quantity, "quantity")
        self._order_counts[dish_name] = self._order_counts.get(dish_name, 0) + quantity

    def times_ordered(self, dish_name: str) -> int:
        return self._order_counts.get(dish_name, 0)

    def favorites(self, limit: int) -> list[str]:
        ranked = sorted(self._order_counts.items(), key=lambda item: (-item[1], item[0]))
        return [name for name, _ in ranked[:limit]]
