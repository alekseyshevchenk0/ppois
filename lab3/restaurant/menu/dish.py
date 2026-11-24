from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from restaurant.catalog.allergen import Allergen
from restaurant.catalog.nutrition import NutritionInfo
from restaurant.exceptions import AllergenConflictError, DishUnavailableError
from restaurant.inventory.inventory import Inventory
from restaurant.menu.recipe import Recipe
from restaurant.money import apply_percent
from restaurant.validation import require_non_empty, require_positive

DEFAULT_FRESHNESS_DAYS = 365


class Dish:
    def __init__(self, name: str, price: Decimal, recipe: Recipe, description: str = "") -> None:
        require_non_empty(name, "название блюда")
        require_positive(price, "цена блюда")
        self.name = name
        self.price = price
        self.recipe = recipe
        self.description = description
        self.is_stopped = False

    def stop(self) -> None:
        self.is_stopped = True

    def resume(self) -> None:
        self.is_stopped = False

    def change_price_by_percent(self, percent: Decimal) -> Decimal:
        new_price = apply_percent(self.price, percent)
        require_positive(new_price, "новая цена блюда")
        self.price = new_price
        return new_price

    def allergens(self) -> frozenset[Allergen]:
        return self.recipe.allergens()

    def is_vegetarian(self) -> bool:
        return self.recipe.is_vegetarian()

    def nutrition(self) -> NutritionInfo:
        return self.recipe.nutrition_per_portion()

    def ensure_safe_for(self, forbidden: Iterable[Allergen]) -> None:
        conflict = self.allergens() & frozenset(forbidden)
        if conflict:
            raise AllergenConflictError(self.name, (allergen.value for allergen in conflict))

    def is_available(self, inventory: Inventory, today: date) -> bool:
        return not self.is_stopped and self.recipe.can_be_cooked(inventory, today)

    def cook(self, inventory: Inventory, today: date) -> None:
        if self.is_stopped:
            raise DishUnavailableError(self.name, "блюдо находится в стоп-листе")
        missing = self.recipe.missing_for(inventory, today)
        if missing:
            names = ", ".join(sorted(ingredient.name for ingredient in missing))
            raise DishUnavailableError(self.name, f"не хватает ингредиентов: {names}")
        inventory.consume_all(self.recipe.requirements_for(1), today)

    def days_until_stock_expires(self, inventory: Inventory, today: date) -> int:
        deadlines = [inventory.earliest_expiry_days(ingredient, today) for ingredient in self.recipe.ingredients()]
        known = [days for days in deadlines if days is not None]
        return min(known, default=DEFAULT_FRESHNESS_DAYS)
