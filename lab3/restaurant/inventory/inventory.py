from __future__ import annotations

from datetime import date
from typing import Callable

from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InsufficientStockError
from restaurant.inventory.stock_item import QUANTITY_EPSILON, StockItem
from restaurant.validation import require_non_negative, require_positive

TARGET_STOCK_MULTIPLIER = 2


class Inventory:

    def __init__(self) -> None:
        self._batches: list[StockItem] = []
        self._reorder_levels: dict[Ingredient, float] = {}
        self._change_callback: Callable[[], None] | None = None

    def set_change_callback(self, callback: Callable[[], None] | None) -> None:
        self._change_callback = callback

    def _notify_change(self) -> None:
        if self._change_callback is not None:
            self._change_callback()

    @property
    def batches(self) -> tuple[StockItem, ...]:
        return tuple(self._batches)

    def receive(self, ingredient: Ingredient, quantity: float, received_on: date) -> StockItem:
        batch = StockItem(ingredient, quantity, received_on)
        self._batches.append(batch)
        self._notify_change()
        return batch

    def set_reorder_level(self, ingredient: Ingredient, level: float) -> None:
        require_non_negative(level, "порог заказа")
        self._reorder_levels[ingredient] = level

    def total_of(self, ingredient: Ingredient, today: date) -> float:
        return sum(batch.quantity for batch in self._fresh_batches(ingredient, today))

    def earliest_expiry_days(self, ingredient: Ingredient, today: date) -> int | None:
        batches = self._fresh_batches(ingredient, today)
        return batches[0].days_until_expiry(today) if batches else None

    def has_enough(self, ingredient: Ingredient, amount: float, today: date) -> bool:
        return self.total_of(ingredient, today) + QUANTITY_EPSILON >= amount

    def consume(self, ingredient: Ingredient, amount: float, today: date) -> None:
        require_positive(amount, "расходуемое количество")
        self._require_available(ingredient, amount, today)
        remaining = amount
        for batch in self._fresh_batches(ingredient, today):
            remaining -= batch.consume(remaining)
            if remaining <= QUANTITY_EPSILON:
                break
        self._batches = [batch for batch in self._batches if not batch.is_empty()]
        self._notify_change()

    def consume_all(self, requirements: dict[Ingredient, float], today: date) -> None:
        for ingredient, amount in requirements.items():
            self._require_available(ingredient, amount, today)
        for ingredient, amount in requirements.items():
            self.consume(ingredient, amount, today)

    def discard_expired(self, today: date) -> list[StockItem]:
        expired = [batch for batch in self._batches if batch.is_expired(today)]
        self._batches = [batch for batch in self._batches if not batch.is_expired(today)]
        if expired:
            self._notify_change()
        return expired

    def expiring_soon(self, today: date, within_days: int) -> list[StockItem]:
        return [
            batch
            for batch in self._batches
            if not batch.is_expired(today) and batch.days_until_expiry(today) <= within_days
        ]

    def shortage_amounts(self, today: date) -> dict[Ingredient, float]:
        shortages: dict[Ingredient, float] = {}
        for ingredient, level in self._reorder_levels.items():
            current = self.total_of(ingredient, today)
            if current < level:
                shortages[ingredient] = level * TARGET_STOCK_MULTIPLIER - current
        return shortages

    def stock_report(self, today: date) -> dict[Ingredient, float]:
        ingredients = {batch.ingredient for batch in self._batches}
        return {ingredient: self.total_of(ingredient, today) for ingredient in ingredients}

    def _fresh_batches(self, ingredient: Ingredient, today: date) -> list[StockItem]:
        fresh = [batch for batch in self._batches if batch.ingredient == ingredient and not batch.is_expired(today)]
        return sorted(fresh, key=lambda batch: batch.expiry_date())

    def _require_available(self, ingredient: Ingredient, amount: float, today: date) -> None:
        if not self.has_enough(ingredient, amount, today):
            raise InsufficientStockError(ingredient.name, amount, self.total_of(ingredient, today))
