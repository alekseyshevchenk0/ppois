from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .constants import (
    ANNUAL_DEPRECIATION,
    BOXSET_DISC_COUNT,
    DEFAULT_SHELF_CAPACITY,
    LP_RPM,
    MIN_CONDITION,
    MINT_CONDITION,
)
from .exceptions import InvalidAmountError, StorageFullError


@dataclass(eq=False)
class PhysicalMedia:
    title: str
    album_title: str
    condition: int = MINT_CONDITION
    purchase_price: float = 0.0

    def degrade(self, amount: int) -> int:
        if amount < 0:
            raise InvalidAmountError("Износ не может быть отрицательным")
        self.condition = max(MIN_CONDITION, self.condition - amount)
        return self.condition

    def depreciated_value(self, years: int) -> float:
        remaining = max(0.0, 1 - ANNUAL_DEPRECIATION * years)
        return round(self.purchase_price * remaining, 2)


@dataclass(eq=False)
class Vinyl(PhysicalMedia):
    rpm: int = LP_RPM

    def is_lp(self) -> bool:
        return self.rpm == LP_RPM


@dataclass(eq=False)
class CompactDisc(PhysicalMedia):
    disc_count: int = 1

    def is_boxset(self) -> bool:
        return self.disc_count >= BOXSET_DISC_COUNT


@dataclass(eq=False)
class Shelf:
    label: str
    capacity: int = DEFAULT_SHELF_CAPACITY
    items: List[PhysicalMedia] = field(default_factory=list)

    def place(self, media: PhysicalMedia) -> None:
        if self.free_slots() == 0:
            raise StorageFullError("На полке нет места")
        self.items.append(media)

    def free_slots(self) -> int:
        return self.capacity - len(self.items)

    def total_value(self) -> float:
        return round(sum(item.purchase_price for item in self.items), 2)
