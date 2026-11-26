from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from restaurant.catalog.allergen import Allergen
from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InvalidDataError
from restaurant.inventory.inventory import Inventory
from restaurant.menu.category import MenuCategory
from restaurant.menu.dish import Dish
from restaurant.validation import require_non_empty


class Menu:
    def __init__(self, name: str) -> None:
        require_non_empty(name, "название меню")
        self.name = name
        self._categories: dict[str, MenuCategory] = {}

    @property
    def categories(self) -> tuple[MenuCategory, ...]:
        return tuple(self._categories.values())

    def add_category(self, category: MenuCategory) -> None:
        if category.name in self._categories:
            raise InvalidDataError(f"Категория «{category.name}» уже существует")
        self._categories[category.name] = category

    def category(self, name: str) -> MenuCategory:
        if name not in self._categories:
            raise InvalidDataError(f"Категория «{name}» не существует")
        return self._categories[name]

    def add_dish(self, category_name: str, dish: Dish) -> None:
        self.category(category_name).add_dish(dish)

    def remove_dish(self, name: str) -> Dish:
        for category in self._categories.values():
            if category.find_dish(name) is not None:
                return category.remove_dish(name)
        raise InvalidDataError(f"Блюдо «{name}» не найдено")

    def all_dishes(self) -> list[Dish]:
        return [dish for category in self._categories.values() for dish in category.dishes]

    def find_dish(self, name: str) -> Dish | None:
        return next((dish for dish in self.all_dishes() if dish.name == name), None)

    def available_dishes(self, inventory: Inventory, today: date) -> list[Dish]:
        return [dish for dish in self.all_dishes() if dish.is_available(inventory, today)]

    def stop_list(self, inventory: Inventory, today: date) -> dict[str, dict[Ingredient, float]]:
        report: dict[str, dict[Ingredient, float]] = {}
        for dish in self.all_dishes():
            missing = dish.recipe.missing_for(inventory, today)
            if missing:
                report[dish.name] = missing
        return report

    def dishes_safe_for(self, forbidden: Iterable[Allergen]) -> list[Dish]:
        forbidden_set = frozenset(forbidden)
        return [dish for dish in self.all_dishes() if not dish.allergens() & forbidden_set]

    def vegetarian_dishes(self) -> list[Dish]:
        return [dish for dish in self.all_dishes() if dish.is_vegetarian()]

    def dishes_in_price_range(self, lowest: Decimal, highest: Decimal) -> list[Dish]:
        return [dish for dish in self.all_dishes() if lowest <= dish.price <= highest]

    def most_expensive_dish(self) -> Dish | None:
        return max(self.all_dishes(), key=lambda dish: dish.price, default=None)
