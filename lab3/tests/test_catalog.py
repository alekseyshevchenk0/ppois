from datetime import date

import pytest

from restaurant.catalog.allergen import Allergen
from restaurant.catalog.ingredient import Ingredient
from restaurant.catalog.nutrition import EMPTY_NUTRITION, NutritionInfo
from restaurant.exceptions import InvalidDataError


def test_nutrition_rejects_negative_values() -> None:
    with pytest.raises(InvalidDataError):
        NutritionInfo(-1, 0, 0, 0)


def test_nutrition_scale_and_combine() -> None:
    base = NutritionInfo(100, 10, 5, 20)
    doubled = base.scale(2)
    assert doubled == NutritionInfo(200, 20, 10, 40)
    assert base.combine(doubled) == NutritionInfo(300, 30, 15, 60)
    assert EMPTY_NUTRITION.combine(base) == base


def test_nutrition_energy_from_macros() -> None:
    assert NutritionInfo(0, 10, 5, 20).energy_from_macros() == 10 * 4 + 5 * 9 + 20 * 4


def test_nutrition_thresholds() -> None:
    nutrition = NutritionInfo(150, 25, 3, 10)
    assert nutrition.is_high_protein(20)
    assert not nutrition.is_high_protein(30)
    assert nutrition.is_low_calorie(200)
    assert not nutrition.is_low_calorie(100)


def test_ingredient_validation() -> None:
    nutrition = NutritionInfo(1, 1, 1, 1)
    with pytest.raises(InvalidDataError):
        Ingredient("", "g", nutrition, 5)
    with pytest.raises(InvalidDataError):
        Ingredient("salt", " ", nutrition, 5)
    with pytest.raises(InvalidDataError):
        Ingredient("salt", "g", nutrition, 0)


def test_ingredient_allergen_and_nutrition(flour: Ingredient) -> None:
    assert flour.contains_allergen(Allergen.GLUTEN)
    assert not flour.contains_allergen(Allergen.MILK)
    assert flour.nutrition_for(100).calories == pytest.approx(360)


def test_ingredient_expiry_date(flour: Ingredient) -> None:
    assert flour.expiry_date(date(2026, 1, 1)) == date(2026, 6, 30)
