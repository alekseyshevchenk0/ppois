from __future__ import annotations

from restaurant.exceptions import InvalidDataError
from restaurant.hall.table import Table
from restaurant.validation import require_non_empty


class Hall:
    def __init__(self, name: str, is_outdoor: bool = False) -> None:
        require_non_empty(name, "название зала")
        self.name = name
        self.is_outdoor = is_outdoor
        self._tables: dict[int, Table] = {}

    @property
    def tables(self) -> list[Table]:
        return [self._tables[number] for number in sorted(self._tables)]

    def add_table(self, table: Table) -> None:
        if table.number in self._tables:
            raise InvalidDataError(f"Стол №{table.number} уже есть в зале «{self.name}»")
        self._tables[table.number] = table

    def remove_table(self, number: int) -> Table:
        if number not in self._tables:
            raise InvalidDataError(f"Стола №{number} нет в зале «{self.name}»")
        return self._tables.pop(number)

    def find_table(self, number: int) -> Table | None:
        return self._tables.get(number)

    def total_capacity(self) -> int:
        return sum(table.capacity for table in self.tables if table.is_in_service)

    def tables_for(self, guests_count: int) -> list[Table]:
        return [table for table in self.tables if table.is_in_service and table.fits(guests_count)]

    def window_tables(self) -> list[Table]:
        return [table for table in self.tables if table.near_window]
