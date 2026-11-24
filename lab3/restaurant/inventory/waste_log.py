from __future__ import annotations

from datetime import date
from restaurant.catalog.ingredient import Ingredient
from restaurant.validation import require_non_empty, require_positive


class WasteLog:
    def __init__(self) -> None:
        self._entries: list[dict[str, object]] = []

    @property
    def entries(self) -> list[dict[str, object]]:
        return [entry.copy() for entry in self._entries]

    def record(self, ingredient: Ingredient, quantity: float, recorded_on: date, reason: str) -> None:
        require_positive(quantity, "количество списания")
        require_non_empty(reason, "причина списания")
        self._entries.append({"ingredient": ingredient, "количество": quantity, "recorded_on": recorded_on, "reason": reason})

    def total_quantity(self, ingredient: Ingredient | None = None) -> float:
        return sum(
            float(entry["количество"])
            for entry in self._entries
            if ingredient is None or entry["ingredient"] == ingredient
        )

    def quantity_by_reason(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for entry in self._entries:
            reason = str(entry["reason"])
            totals[reason] = totals.get(reason, 0.0) + float(entry["количество"])
        return totals
