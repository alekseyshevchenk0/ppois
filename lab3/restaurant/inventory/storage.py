from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InvalidDataError
from restaurant.inventory.inventory import Inventory


class InventoryStorage:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self, inventory: Inventory, ingredients: dict[str, Ingredient]) -> bool:
        if not self.path.exists():
            return False
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            for batch in data["batches"]:
                ingredient = ingredients[batch["ingredient"]]
                inventory.receive(
                    ingredient,
                    float(batch["quantity"]),
                    date.fromisoformat(batch["received_on"]),
                )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            message = "Файл склада повреждён или содержит неизвестные ингредиенты"
            raise InvalidDataError(message) from error
        return True

    def save(self, inventory: Inventory) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "batches": [
                {
                    "ingredient": batch.ingredient.name,
                    "quantity": batch.quantity,
                    "received_on": batch.received_on.isoformat(),
                }
                for batch in inventory.batches
            ]
        }
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )
