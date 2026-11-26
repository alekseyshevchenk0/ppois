from __future__ import annotations

from datetime import date
from decimal import Decimal

from restaurant.money import CENT, percent_of
from restaurant.staff.employee import Employee
from restaurant.staff.schedule import Schedule

OVERTIME_THRESHOLD_HOURS = 40.0
OVERTIME_MULTIPLIER = Decimal("1.5")
NIGHT_BONUS_PERCENT = Decimal(20)
TAX_PERCENT = Decimal(13)


class Payroll:
    def __init__(
        self,
        schedule: Schedule,
        overtime_threshold_hours: float = OVERTIME_THRESHOLD_HOURS,
        overtime_multiplier: Decimal = OVERTIME_MULTIPLIER,
        night_bonus_percent: Decimal = NIGHT_BONUS_PERCENT,
        tax_percent: Decimal = TAX_PERCENT,
    ) -> None:
        self.schedule = schedule
        self.overtime_threshold_hours = overtime_threshold_hours
        self.overtime_multiplier = overtime_multiplier
        self.night_bonus_percent = night_bonus_percent
        self.tax_percent = tax_percent

    def overtime_hours(self, employee: Employee, week_start: date) -> float:
        worked = self.schedule.weekly_hours(employee, week_start)
        return max(0.0, worked - self.overtime_threshold_hours)

    def night_bonus(self, employee: Employee, week_start: date) -> Decimal:
        night_hours = sum(shift.night_hours() for shift in self.schedule.week_shifts(employee, week_start))
        night_pay = employee.hourly_rate * Decimal(str(night_hours))
        return percent_of(night_pay, self.night_bonus_percent)

    def gross_pay(self, employee: Employee, week_start: date) -> Decimal:
        overtime = self.overtime_hours(employee, week_start)
        regular = self.schedule.weekly_hours(employee, week_start) - overtime
        regular_pay = employee.hourly_rate * Decimal(str(regular))
        overtime_pay = employee.hourly_rate * self.overtime_multiplier * Decimal(str(overtime))
        return (regular_pay + overtime_pay + self.night_bonus(employee, week_start)).quantize(CENT)

    def payslip(self, employee: Employee, week_start: date) -> dict[str, Decimal]:
        gross = self.gross_pay(employee, week_start)
        tax = percent_of(gross, self.tax_percent)
        return {"gross": gross, "tax": tax, "net": gross - tax}
