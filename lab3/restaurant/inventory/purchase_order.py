from __future__ import annotations

from datetime import date
from decimal import Decimal

from restaurant.catalog.ingredient import Ingredient
from restaurant.exceptions import InvalidDataError
from restaurant.inventory.inventory import Inventory
from restaurant.inventory.supplier import Supplier
from restaurant.validation import require_positive


class PurchaseOrder:
    def __init__(self, supplier: Supplier, created_on: date) -> None:
        self.supplier = supplier
        self.created_on = created_on
        self.is_received = False
        self._lines: dict[Ingredient, float] = {}

    @classmethod
    def for_shortages(cls, supplier: Supplier, inventory: Inventory, today: date) -> PurchaseOrder:
        order = cls(supplier, today)
        for ingredient, amount in inventory.shortage_amounts(today).items():
            if supplier.supplies(ingredient):
                order.add_line(ingredient, amount)
        return order

    @property
    def lines(self) -> dict[Ingredient, float]:
        return dict(self._lines)

    def add_line(self, ingredient: Ingredient, amount: float) -> None:
        require_positive(amount, "заказываемое количество")
        if not self.supplier.supplies(ingredient):
            raise InvalidDataError(f"Поставщик «{self.supplier.name}» не продаёт ингредиент «{ingredient.name}»")
        self._lines[ingredient] = self._lines.get(ingredient, 0.0) + amount

    def total_cost(self) -> Decimal:
        return sum(
            (self.supplier.quote(ingredient, amount) for ingredient, amount in self._lines.items()),
            Decimal(0),
        )

    def expected_delivery(self) -> date:
        return self.supplier.delivery_date(self.created_on)

    def receive_into(self, inventory: Inventory, received_on: date) -> None:
        if self.is_received:
            raise InvalidDataError("Заказ поставщику уже принят")
        for ingredient, amount in self._lines.items():
            inventory.receive(ingredient, amount, received_on)
        self.is_received = True
