from __future__ import annotations

from datetime import date
from decimal import Decimal

from restaurant.exceptions import InvalidDataError
from restaurant.inventory.inventory import Inventory
from restaurant.menu.dish import Dish
from restaurant.validation import require_non_empty


class MenuCategory:
    def __init__(self, name: str) -> None:
        require_non_empty(name, "category name")
        self.name = name
        self._dishes: list[Dish] = []

    @property
    def dishes(self) -> tuple[Dish, ...]:
        return tuple(self._dishes)

    def add_dish(self, dish: Dish) -> None:
        if self.find_dish(dish.name) is not None:
            raise InvalidDataError(f"Dish '{dish.name}' is already in category '{self.name}'")
        self._dishes.append(dish)

    def remove_dish(self, name: str) -> Dish:
        dish = self.find_dish(name)
        if dish is None:
            raise InvalidDataError(f"Dish '{name}' is not in category '{self.name}'")
        self._dishes.remove(dish)
        return dish

    def find_dish(self, name: str) -> Dish | None:
        return next((dish for dish in self._dishes if dish.name == name), None)

    def average_price(self) -> Decimal:
        if not self._dishes:
            return Decimal(0)
        return sum((dish.price for dish in self._dishes), Decimal(0)) / len(self._dishes)

    def cheapest_dish(self) -> Dish | None:
        return min(self._dishes, key=lambda dish: dish.price, default=None)

    def available_dishes(self, inventory: Inventory, today: date) -> list[Dish]:
        return [dish for dish in self._dishes if dish.is_available(inventory, today)]
