from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from restaurant.exceptions import InvalidDataError, TableUnavailableError
from restaurant.guests.customer import Customer
from restaurant.hall.hall import Hall
from restaurant.hall.reservation import Reservation
from restaurant.hall.reservation_book import ReservationBook
from restaurant.hall.table import Table
from restaurant.money import CENT, apply_percent, percent_of
from restaurant.validation import require_positive

BANQUET_DURATION_MINUTES = 240
LARGE_BANQUET_GUESTS = 30
LARGE_BANQUET_DISCOUNT_PERCENT = Decimal(5)
DEPOSIT_PERCENT = Decimal(30)


class Banquet:
    def __init__(
        self,
        organizer: Customer,
        hall: Hall,
        start: datetime,
        guests_count: int,
        price_per_guest: Decimal,
        duration_minutes: int = BANQUET_DURATION_MINUTES,
    ) -> None:
        require_positive(guests_count, "количество гостей")
        require_positive(price_per_guest, "цена на одного гостя")
        self.organizer = organizer
        self.hall = hall
        self.start = start
        self.guests_count = guests_count
        self.price_per_guest = price_per_guest
        self.duration_minutes = duration_minutes
        self._reservations: list[Reservation] = []

    def required_tables(self, book: ReservationBook) -> list[Table]:
        free = book.free_tables(self.hall, self.start, self.duration_minutes, 1)
        chosen: list[Table] = []
        seats = 0
        for table in sorted(free, key=lambda candidate: -candidate.capacity):
            if seats >= self.guests_count:
                break
            chosen.append(table)
            seats += table.capacity
        if seats < self.guests_count:
            raise TableUnavailableError(f"Зал «{self.hall.name}»", f"не хватает столов для {self.guests_count} гостей")
        return chosen

    def confirm(self, book: ReservationBook) -> list[Reservation]:
        if self.is_confirmed():
            raise InvalidDataError("Банкет уже подтверждён")
        remaining = self.guests_count
        for table in self.required_tables(book):
            seated = min(table.capacity, remaining)
            self._reservations.append(book.book(self.organizer, table, self.start, seated, self.duration_minutes))
            remaining -= seated
        return list(self._reservations)

    def is_confirmed(self) -> bool:
        return any(reservation.is_active() for reservation in self._reservations)

    def cancel(self) -> None:
        for reservation in self._reservations:
            reservation.cancel()

    def total_price(self) -> Decimal:
        total = self.price_per_guest * self.guests_count
        if self.guests_count >= LARGE_BANQUET_GUESTS:
            return apply_percent(total, -LARGE_BANQUET_DISCOUNT_PERCENT)
        return total.quantize(CENT)

    def deposit_amount(self) -> Decimal:
        return percent_of(self.total_price(), DEPOSIT_PERCENT)
