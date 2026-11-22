from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal

from restaurant.staff.employee import Employee
from restaurant.staff.schedule import Schedule
from restaurant.staff.shift import Shift


@dataclass(frozen=True)
class ApprovalLimits:

    max_discount_percent: Decimal
    refund_limit: Decimal
    max_overtime_hours: float


class Manager(Employee):
    role_title = "manager"

    def __init__(
        self, name: str, phone: str, birth_date: date, hourly_rate: Decimal, hire_date: date, limits: ApprovalLimits
    ) -> None:
        super().__init__(name, phone, birth_date, hourly_rate, hire_date)
        self.limits = limits
        self.approvals_count = 0

    def can_approve_discount(self, percent: Decimal) -> bool:
        return percent <= self.limits.max_discount_percent

    def can_approve_refund(self, amount: Decimal) -> bool:
        return amount <= self.limits.refund_limit

    def approve_overtime(self, hours: float) -> bool:
        approved = hours <= self.limits.max_overtime_hours
        if approved:
            self.approvals_count += 1
        return approved

    def assign_shift(self, schedule: Schedule, employee: Employee, day: date, start: time, end: time) -> Shift:
        shift = Shift(employee, day, start, end)
        schedule.add_shift(shift)
        self.approvals_count += 1
        return shift
