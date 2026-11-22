from __future__ import annotations

from datetime import datetime, timedelta

from restaurant.exceptions import TableUnavailableError
from restaurant.guests.customer import Customer
from restaurant.hall.table import Table
from restaurant.validation import require_positive

DEFAULT_DURATION_MINUTES = 120
NO_SHOW_GRACE_MINUTES = 15


class Reservation:
    def __init__(
        self, guest: Customer, table: Table, start: datetime, guests_count: int, duration_minutes: int = DEFAULT_DURATION_MINUTES
    ) -> None:
        require_positive(guests_count, "guests count")
        require_positive(duration_minutes, "reservation duration")
        if not table.fits(guests_count):
            raise TableUnavailableError(table.label(), f"не хватает мест для {guests_count} гостей")
        self.guest = guest
        self.table = table
        self.start = start
        self.guests_count = guests_count
        self.duration_minutes = duration_minutes
        self.is_cancelled = False
        self.has_arrived = False

    def end_time(self) -> datetime:
        return self.start + timedelta(minutes=self.duration_minutes)

    def is_active(self) -> bool:
        return not self.is_cancelled

    def overlaps_with(self, start: datetime, end: datetime) -> bool:
        return self.start < end and start < self.end_time()

    def cancel(self) -> None:
        self.is_cancelled = True

    def mark_arrived(self) -> None:
        self.has_arrived = True

    def is_no_show(self, now: datetime) -> bool:
        deadline = self.start + timedelta(minutes=NO_SHOW_GRACE_MINUTES)
        return self.is_active() and not self.has_arrived and now > deadline
