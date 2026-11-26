from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta

from restaurant.guests.customer import Customer
from restaurant.hall.hall import Hall
from restaurant.hall.reservation import DEFAULT_DURATION_MINUTES, Reservation
from restaurant.hall.reservation_book import ReservationBook
from restaurant.hall.table import Table
from restaurant.hall.waitlist import Waitlist

WASTED_SEAT_PENALTY = 10
WINDOW_BONUS = 15
SUGGESTION_STEP_MINUTES = 30
SUGGESTION_COUNT = 3
SUGGESTION_SEARCH_STEPS = 12


class SeatingPlanner:
    def __init__(self, halls: Iterable[Hall], reservations: ReservationBook, waitlist: Waitlist) -> None:
        self.halls = list(halls)
        self.reservations = reservations
        self.waitlist = waitlist

    def candidate_tables(self, start: datetime, guests_count: int, duration_minutes: int) -> list[Table]:
        candidates: list[Table] = []
        for hall in self.halls:
            candidates.extend(self.reservations.free_tables(hall, start, duration_minutes, guests_count))
        return candidates

    def score(self, table: Table, guests_count: int, prefer_window: bool) -> int:
        score = table.wasted_seats(guests_count) * WASTED_SEAT_PENALTY
        if prefer_window and table.near_window:
            score -= WINDOW_BONUS
        return score

    def best_table(
        self, start: datetime, guests_count: int, duration_minutes: int = DEFAULT_DURATION_MINUTES, prefer_window: bool = False
    ) -> Table | None:
        candidates = self.candidate_tables(start, guests_count, duration_minutes)
        return min(candidates, key=lambda table: (self.score(table, guests_count, prefer_window), table.number), default=None)

    def seat_or_wait(
        self,
        guest: Customer,
        guests_count: int,
        start: datetime,
        now: datetime,
        duration_minutes: int = DEFAULT_DURATION_MINUTES,
        prefer_window: bool = False,
    ) -> Reservation | None:
        table = self.best_table(start, guests_count, duration_minutes, prefer_window)
        if table is None:
            self.waitlist.join(guest, guests_count, now)
            return None
        return self.reservations.book(guest, table, start, guests_count, duration_minutes)

    def promote_from_waitlist(self, table: Table, start: datetime, duration_minutes: int = DEFAULT_DURATION_MINUTES) -> Reservation | None:
        entry = self.waitlist.next_for(table)
        if entry is None or not self.reservations.is_table_free(table, start, duration_minutes):
            return None
        self.waitlist.leave(entry.guest)
        return self.reservations.book(entry.guest, table, start, entry.guests_count, duration_minutes)

    def suggest_alternative_times(
        self, guests_count: int, start: datetime, duration_minutes: int = DEFAULT_DURATION_MINUTES
    ) -> list[datetime]:
        suggestions: list[datetime] = []
        for step in range(1, SUGGESTION_SEARCH_STEPS + 1):
            moment = start + timedelta(minutes=step * SUGGESTION_STEP_MINUTES)
            if self.best_table(moment, guests_count, duration_minutes) is not None:
                suggestions.append(moment)
            if len(suggestions) == SUGGESTION_COUNT:
                break
        return suggestions
