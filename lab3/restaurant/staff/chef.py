from __future__ import annotations

from datetime import date
from decimal import Decimal

from restaurant.inventory.inventory import Inventory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu
from restaurant.staff.employee import Employee
from restaurant.validation import require_non_empty


class Chef(Employee):
    role_title = "chef"

    def __init__(self, name: str, phone: str, birth_date: date, hourly_rate: Decimal, hire_date: date, cuisine: str) -> None:
        super().__init__(name, phone, birth_date, hourly_rate, hire_date)
        require_non_empty(cuisine, "cuisine")
        self.cuisine = cuisine
        self._approved: set[str] = set()

    def approve(self, dish: Dish) -> None:
        self._approved.add(dish.name)

    def revoke(self, dish: Dish) -> None:
        self._approved.discard(dish.name)

    def has_approved(self, dish: Dish) -> bool:
        return dish.name in self._approved

    def suggest_special(self, menu: Menu, inventory: Inventory, today: date) -> Dish | None:
        candidates = [dish for dish in menu.available_dishes(inventory, today) if self.has_approved(dish)]
        return min(candidates, key=lambda dish: dish.days_until_stock_expires(inventory, today), default=None)
