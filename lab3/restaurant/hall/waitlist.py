from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from restaurant.exceptions import InvalidDataError
from restaurant.guests.customer import Customer
from restaurant.hall.table import Table
from restaurant.timeunits import SECONDS_IN_MINUTE
from restaurant.validation import require_positive


@dataclass(frozen=True)
class WaitlistEntry:
    guest: Customer
    guests_count: int
    joined_at: datetime

    def waited_minutes(self, now: datetime) -> int:
        return int((now - self.joined_at).total_seconds() // SECONDS_IN_MINUTE)


class Waitlist:
    def __init__(self) -> None:
        self._entries: list[WaitlistEntry] = []

    def __len__(self) -> int:
        return len(self._entries)

    def join(self, guest: Customer, guests_count: int, joined_at: datetime) -> WaitlistEntry:
        require_positive(guests_count, "количество гостей")
        if self._find(guest) is not None:
            raise InvalidDataError(f"Гость «{guest.name}» уже в листе ожидания")
        entry = WaitlistEntry(guest, guests_count, joined_at)
        self._entries.append(entry)
        return entry

    def leave(self, guest: Customer) -> None:
        self._entries.remove(self._require(guest))

    def ordered(self) -> list[WaitlistEntry]:
        return sorted(self._entries, key=lambda entry: entry.joined_at)

    def position_of(self, guest: Customer) -> int:
        return self.ordered().index(self._require(guest)) + 1

    def estimated_wait_minutes(self, guest: Customer, tables_count: int, turnover_minutes: int) -> int:
        require_positive(tables_count, "количество столов")
        waves = (self.position_of(guest) - 1) // tables_count + 1
        return waves * turnover_minutes

    def next_for(self, table: Table) -> WaitlistEntry | None:
        return next((entry for entry in self.ordered() if table.fits(entry.guests_count)), None)

    def take_next_for(self, table: Table) -> WaitlistEntry | None:
        entry = self.next_for(table)
        if entry is not None:
            self._entries.remove(entry)
        return entry

    def _find(self, guest: Customer) -> WaitlistEntry | None:
        return next((entry for entry in self._entries if entry.guest is guest), None)

    def _require(self, guest: Customer) -> WaitlistEntry:
        entry = self._find(guest)
        if entry is None:
            raise InvalidDataError(f"Гостя «{guest.name}» нет в листе ожидания")
        return entry
