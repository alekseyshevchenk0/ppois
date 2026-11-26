from __future__ import annotations

from datetime import date, datetime, timedelta

from restaurant.exceptions import ReservationConflictError, TableUnavailableError
from restaurant.guests.customer import Customer
from restaurant.hall.hall import Hall
from restaurant.hall.reservation import DEFAULT_DURATION_MINUTES, Reservation
from restaurant.hall.table import Table


class ReservationBook:
    def __init__(self) -> None:
        self._reservations: list[Reservation] = []

    def is_table_free(self, table: Table, start: datetime, duration_minutes: int) -> bool:
        end = start + timedelta(minutes=duration_minutes)
        busy = any(
            booked.table is table and booked.is_active() and booked.overlaps_with(start, end)
            for booked in self._reservations
        )
        return table.is_in_service and not busy

    def book(
        self, guest: Customer, table: Table, start: datetime, guests_count: int, duration_minutes: int = DEFAULT_DURATION_MINUTES
    ) -> Reservation:
        if not table.is_in_service:
            raise TableUnavailableError(table.label(), "стол выведен из эксплуатации")
        if not self.is_table_free(table, start, duration_minutes):
            raise ReservationConflictError(table.number, start)
        reservation = Reservation(guest, table, start, guests_count, duration_minutes)
        self._reservations.append(reservation)
        return reservation

    def cancel(self, reservation: Reservation) -> None:
        reservation.cancel()

    def reservations_of(self, guest: Customer) -> list[Reservation]:
        return [booked for booked in self._reservations if booked.guest is guest and booked.is_active()]

    def reservations_on(self, day: date) -> list[Reservation]:
        return [booked for booked in self._reservations if booked.is_active() and booked.start.date() == day]

    def free_tables(self, hall: Hall, start: datetime, duration_minutes: int, guests_count: int) -> list[Table]:
        return [table for table in hall.tables_for(guests_count) if self.is_table_free(table, start, duration_minutes)]

    def no_shows(self, now: datetime) -> list[Reservation]:
        return [booked for booked in self._reservations if booked.is_no_show(now)]

    def release_no_shows(self, now: datetime) -> int:
        missed = self.no_shows(now)
        for reservation in missed:
            reservation.cancel()
        return len(missed)
