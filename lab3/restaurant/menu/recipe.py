from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import date

from restaurant.catalog.allergen import Allergen
from restaurant.catalog.ingredient import Ingredient
from restaurant.catalog.nutrition import EMPTY_NUTRITION, NutritionInfo
from restaurant.exceptions import InvalidDataError
from restaurant.inventory.inventory import Inventory
from restaurant.inventory.stock_item import QUANTITY_EPSILON
from restaurant.validation import require_non_empty, require_positive

DEFAULT_STATION = "горячий цех"


class Recipe:
    def __init__(self, steps: Sequence[str], cooking_minutes: int, portions: int = 1, station: str = DEFAULT_STATION) -> None:
        if not steps:
            raise InvalidDataError("Рецепт должен содержать хотя бы один шаг")
        require_positive(cooking_minutes, "время приготовления")
        require_positive(portions, "количество порций")
        require_non_empty(station, "станция")
        self.station = station
        self.steps = list(steps)
        self.cooking_minutes = cooking_minutes
        self.portions = portions
        self._requirements: dict[Ingredient, float] = {}

    def add_requirement(self, ingredient: Ingredient, amount: float) -> None:
        require_positive(amount, "количество ингредиента")
        self._requirements[ingredient] = self._requirements.get(ingredient, 0.0) + amount

    def ingredients(self) -> tuple[Ingredient, ...]:
        return tuple(self._requirements)

    def requirements_for(self, portions: int) -> dict[Ingredient, float]:
        require_positive(portions, "количество порций")
        factor = portions / self.portions
        return {ingredient: amount * factor for ingredient, amount in self._requirements.items()}

    def allergens(self) -> frozenset[Allergen]:
        found: set[Allergen] = set()
        for ingredient in self._requirements:
            found |= ingredient.allergens
        return frozenset(found)

    def is_vegetarian(self) -> bool:
        return not any(ingredient.is_animal_origin for ingredient in self._requirements)

    def nutrition_per_portion(self) -> NutritionInfo:
        total = EMPTY_NUTRITION
        for ingredient, amount in self._requirements.items():
            total = total.combine(ingredient.nutrition_for(amount))
        return total.scale(1 / self.portions)

    def cooking_time_for(self, portions: int) -> int:
        """Minutes needed for `portions` portions: the dish is cooked in whole batches."""
        require_positive(portions, "количество порций")
        return self.cooking_minutes * math.ceil(portions / self.portions)

    def missing_for(self, inventory: Inventory, today: date, portions: int = 1) -> dict[Ingredient, float]:
        missing: dict[Ingredient, float] = {}
        for ingredient, needed in self.requirements_for(portions).items():
            available = inventory.total_of(ingredient, today)
            if available < needed - QUANTITY_EPSILON:
                missing[ingredient] = needed - available
        return missing

    def can_be_cooked(self, inventory: Inventory, today: date, portions: int = 1) -> bool:
        return not self.missing_for(inventory, today, portions)
