from __future__ import annotations

from datetime import date, time, timedelta

from restaurant.exceptions import EmployeeNotAvailableError
from restaurant.staff.employee import Employee
from restaurant.staff.shift import Shift

DAYS_IN_WEEK = 7


class Schedule:
    def __init__(self) -> None:
        self._shifts: list[Shift] = []

    def add_shift(self, shift: Shift) -> None:
        shift.employee.ensure_active()
        clashes = any(known.employee is shift.employee and known.overlaps(shift) for known in self._shifts)
        if clashes:
            raise EmployeeNotAvailableError(shift.employee.name, "уже назначена пересекающаяся смена")
        self._shifts.append(shift)

    def remove_shift(self, shift: Shift) -> None:
        self._shifts.remove(shift)

    def shifts_on(self, day: date) -> list[Shift]:
        return [shift for shift in self._shifts if shift.day == day]

    def shifts_of(self, employee: Employee) -> list[Shift]:
        return [shift for shift in self._shifts if shift.employee is employee]

    def on_duty_at(self, day: date, moment: time) -> list[Employee]:
        return [shift.employee for shift in self.shifts_on(day) if shift.covers(moment)]

    def week_shifts(self, employee: Employee, week_start: date) -> list[Shift]:
        week_end = week_start + timedelta(days=DAYS_IN_WEEK)
        return [shift for shift in self.shifts_of(employee) if week_start <= shift.day < week_end]

    def weekly_hours(self, employee: Employee, week_start: date) -> float:
        return sum(shift.duration_hours() for shift in self.week_shifts(employee, week_start))
