from datetime import date

import pytest

from restaurant.catalog.allergen import Allergen
from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InvalidDataError
from restaurant.inventory.inventory import Inventory
from restaurant.menu.recipe import Recipe


def test_recipe_validation() -> None:
    with pytest.raises(InvalidDataError):
        Recipe([], cooking_minutes=5)
    with pytest.raises(InvalidDataError):
        Recipe(["Cook"], cooking_minutes=0)
    with pytest.raises(InvalidDataError):
        Recipe(["Cook"], cooking_minutes=5, portions=0)


def test_requirements_scale_with_portions(pancake_recipe: Recipe, flour: Ingredient) -> None:
    assert pancake_recipe.requirements_for(4)[flour] == pytest.approx(400)
    with pytest.raises(InvalidDataError):
        pancake_recipe.requirements_for(0)


def test_add_requirement_accumulates(salad_recipe: Recipe, tomato: Ingredient) -> None:
    salad_recipe.add_requirement(tomato, 50)
    assert salad_recipe.requirements_for(1)[tomato] == 200
    with pytest.raises(InvalidDataError):
        salad_recipe.add_requirement(tomato, -1)


def test_allergens_and_vegetarian(pancake_recipe: Recipe, salad_recipe: Recipe) -> None:
    assert pancake_recipe.allergens() == {Allergen.GLUTEN, Allergen.MILK}
    assert not pancake_recipe.is_vegetarian()
    assert salad_recipe.is_vegetarian()


def test_nutrition_per_portion(pancake_recipe: Recipe) -> None:
    nutrition = pancake_recipe.nutrition_per_portion()
    assert nutrition.calories == pytest.approx((200 * 3.6 + 300 * 0.6) / 2)


def test_cooking_time_counts_whole_batches(pancake_recipe: Recipe) -> None:
    assert pancake_recipe.cooking_time_for(1) == 10
    assert pancake_recipe.cooking_time_for(2) == 10
    assert pancake_recipe.cooking_time_for(3) == 20
    with pytest.raises(InvalidDataError):
        pancake_recipe.cooking_time_for(0)


def test_missing_ingredients(
    pancake_recipe: Recipe, inventory: Inventory, flour: Ingredient, milk: Ingredient, today: date
) -> None:
    inventory.receive(flour, 500, today)
    inventory.receive(milk, 100, today)
    assert pancake_recipe.missing_for(inventory, today) == {milk: pytest.approx(50)}
    assert not pancake_recipe.can_be_cooked(inventory, today)
    inventory.receive(milk, 1000, today)
    assert pancake_recipe.can_be_cooked(inventory, today)


def test_recipe_lists_its_ingredients(pancake_recipe: Recipe, flour: Ingredient, milk: Ingredient) -> None:
    assert set(pancake_recipe.ingredients()) == {flour, milk}
