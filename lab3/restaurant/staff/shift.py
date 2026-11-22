"""A working shift of one employee."""
from __future__ import annotations

from datetime import date, time

from restaurant.exceptions import InvalidDataError
from restaurant.staff.employee import Employee
from restaurant.timeunits import MINUTES_IN_HOUR

NIGHT_START_HOUR = 22
NIGHT_END_HOUR = 6
HOURS_IN_DAY = 24


def to_hours(moment: time) -> float:
    return moment.hour + moment.minute / MINUTES_IN_HOUR


def overlap_hours(first_start: float, first_end: float, second_start: float, second_end: float) -> float:
    return max(0.0, min(first_end, second_end) - max(first_start, second_start))


class Shift:
    """One employee works on one day from `start` to `end` (shifts do not cross midnight)."""

    def __init__(self, employee: Employee, day: date, start: time, end: time) -> None:
        if end <= start:
            raise InvalidDataError("Shift must end after it starts")
        self.employee = employee
        self.day = day
        self.start = start
        self.end = end

    def duration_hours(self) -> float:
        return to_hours(self.end) - to_hours(self.start)

    def overlaps(self, other: Shift) -> bool:
        return self.day == other.day and self.start < other.end and other.start < self.end

    def covers(self, moment: time) -> bool:
        return self.start <= moment < self.end

    def night_hours(self) -> float:
        start, end = to_hours(self.start), to_hours(self.end)
        evening = overlap_hours(start, end, NIGHT_START_HOUR, HOURS_IN_DAY)
        morning = overlap_hours(start, end, 0, NIGHT_END_HOUR)
        return evening + morning
