from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from restaurant.catalog.allergen import Allergen
from restaurant.catalog.nutrition import NutritionInfo
from restaurant.validation import require_non_empty, require_positive


@dataclass(frozen=True)
class Ingredient:
    name: str
    unit: str
    nutrition_per_unit: NutritionInfo
    shelf_life_days: int
    allergens: frozenset[Allergen] = frozenset()
    is_animal_origin: bool = False

    def __post_init__(self) -> None:
        require_non_empty(self.name, "название ингредиента")
        require_non_empty(self.unit, "единица измерения")
        require_positive(self.shelf_life_days, "срок хранения")

    def contains_allergen(self, allergen: Allergen) -> bool:
        return allergen in self.allergens

    def nutrition_for(self, amount: float) -> NutritionInfo:
        return self.nutrition_per_unit.scale(amount)

    def expiry_date(self, received_on: date) -> date:
        return received_on + timedelta(days=self.shelf_life_days)
