from __future__ import annotations

from restaurant.exceptions import TableUnavailableError
from restaurant.validation import require_positive


class Table:
    def __init__(self, number: int, capacity: int, near_window: bool = False) -> None:
        require_positive(number, "номер стола")
        require_positive(capacity, "вместимость стола")
        self.number = number
        self.capacity = capacity
        self.near_window = near_window
        self.is_in_service = True

    def label(self) -> str:
        return f"Стол №{self.number}"

    def fits(self, guests_count: int) -> bool:
        return guests_count <= self.capacity

    def wasted_seats(self, guests_count: int) -> int:
        if not self.fits(guests_count):
            raise TableUnavailableError(self.label(), f"не хватает мест для {guests_count} гостей")
        return self.capacity - guests_count

    def take_out_of_service(self) -> None:
        self.is_in_service = False

    def return_to_service(self) -> None:
        self.is_in_service = True
