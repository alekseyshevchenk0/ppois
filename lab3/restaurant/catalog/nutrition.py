from __future__ import annotations

from dataclasses import dataclass

from restaurant.exceptions import InvalidDataError

KCAL_PER_GRAM_PROTEIN = 4
KCAL_PER_GRAM_CARBS = 4
KCAL_PER_GRAM_FAT = 9


@dataclass(frozen=True)
class NutritionInfo:

    calories: float
    proteins: float
    fats: float
    carbs: float

    def __post_init__(self) -> None:
        values = (self.calories, self.proteins, self.fats, self.carbs)
        if any(value < 0 for value in values):
            raise InvalidDataError("Nutrition values must not be negative")

    def scale(self, factor: float) -> NutritionInfo:
        return NutritionInfo(self.calories * factor, self.proteins * factor, self.fats * factor, self.carbs * factor)

    def combine(self, other: NutritionInfo) -> NutritionInfo:
        return NutritionInfo(
            self.calories + other.calories,
            self.proteins + other.proteins,
            self.fats + other.fats,
            self.carbs + other.carbs,
        )

    def energy_from_macros(self) -> float:
        return self.proteins * KCAL_PER_GRAM_PROTEIN + self.carbs * KCAL_PER_GRAM_CARBS + self.fats * KCAL_PER_GRAM_FAT

    def is_high_protein(self, min_proteins: float) -> bool:
        return self.proteins >= min_proteins

    def is_low_calorie(self, max_calories: float) -> bool:
        return self.calories <= max_calories


EMPTY_NUTRITION = NutritionInfo(0, 0, 0, 0)
