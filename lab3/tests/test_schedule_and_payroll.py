from datetime import date, time, timedelta
from decimal import Decimal

import pytest

from restaurant.exceptions import EmployeeNotAvailableError, InvalidDataError
from restaurant.staff.cook import Cook
from restaurant.staff.payroll import Payroll
from restaurant.staff.schedule import Schedule
from restaurant.staff.shift import Shift
from restaurant.staff.waiter import Waiter

MONDAY = date(2026, 11, 16)


def test_shift_must_end_after_start(waiter: Waiter) -> None:
    with pytest.raises(InvalidDataError):
        Shift(waiter, MONDAY, time(17), time(9))


def test_shift_duration_and_cover(waiter: Waiter) -> None:
    shift = Shift(waiter, MONDAY, time(9, 30), time(17))
    assert shift.duration_hours() == pytest.approx(7.5)
    assert shift.covers(time(9, 30))
    assert not shift.covers(time(17))


def test_shift_overlap(waiter: Waiter) -> None:
    morning = Shift(waiter, MONDAY, time(8), time(14))
    assert morning.overlaps(Shift(waiter, MONDAY, time(13), time(20)))
    assert not morning.overlaps(Shift(waiter, MONDAY, time(14), time(20)))
    assert not morning.overlaps(Shift(waiter, MONDAY + timedelta(days=1), time(8), time(14)))


def test_night_hours(waiter: Waiter) -> None:
    assert Shift(waiter, MONDAY, time(18), time(23, 30)).night_hours() == pytest.approx(1.5)
    assert Shift(waiter, MONDAY, time(4), time(10)).night_hours() == pytest.approx(2)
    assert Shift(waiter, MONDAY, time(9), time(17)).night_hours() == 0


def test_schedule_rejects_overlap_and_dismissed(waiter: Waiter, cook: Cook) -> None:
    schedule = Schedule()
    schedule.add_shift(Shift(waiter, MONDAY, time(8), time(14)))
    with pytest.raises(EmployeeNotAvailableError):
        schedule.add_shift(Shift(waiter, MONDAY, time(13), time(18)))
    schedule.add_shift(Shift(cook, MONDAY, time(13), time(18)))
    cook.dismiss()
    with pytest.raises(EmployeeNotAvailableError):
        schedule.add_shift(Shift(cook, MONDAY + timedelta(days=1), time(8), time(12)))


def test_schedule_queries(waiter: Waiter, cook: Cook) -> None:
    schedule = Schedule()
    waiter_shift = Shift(waiter, MONDAY, time(8), time(14))
    schedule.add_shift(waiter_shift)
    schedule.add_shift(Shift(cook, MONDAY, time(12), time(20)))
    assert schedule.on_duty_at(MONDAY, time(13)) == [waiter, cook]
    assert schedule.on_duty_at(MONDAY, time(19)) == [cook]
    assert len(schedule.shifts_on(MONDAY)) == 2
    schedule.remove_shift(waiter_shift)
    assert schedule.shifts_of(waiter) == []


def test_weekly_hours_ignore_other_weeks(waiter: Waiter) -> None:
    schedule = Schedule()
    schedule.add_shift(Shift(waiter, MONDAY, time(8), time(16)))
    schedule.add_shift(Shift(waiter, MONDAY + timedelta(days=7), time(8), time(16)))
    assert schedule.weekly_hours(waiter, MONDAY) == 8
    assert len(schedule.week_shifts(waiter, MONDAY)) == 1


def week_of_eight_hour_shifts(waiter: Waiter, days: int) -> Schedule:
    schedule = Schedule()
    for offset in range(days):
        schedule.add_shift(Shift(waiter, MONDAY + timedelta(days=offset), time(9), time(17)))
    return schedule


def test_payroll_with_overtime(waiter: Waiter) -> None:
    payroll = Payroll(week_of_eight_hour_shifts(waiter, 6))
    assert payroll.overtime_hours(waiter, MONDAY) == 8
    assert payroll.gross_pay(waiter, MONDAY) == Decimal("520.00")
    assert payroll.payslip(waiter, MONDAY) == {"gross": Decimal("520.00"), "tax": Decimal("67.60"), "net": Decimal("452.40")}


def test_payroll_without_overtime(waiter: Waiter) -> None:
    payroll = Payroll(week_of_eight_hour_shifts(waiter, 2))
    assert payroll.overtime_hours(waiter, MONDAY) == 0
    assert payroll.gross_pay(waiter, MONDAY) == Decimal("160.00")


def test_payroll_night_bonus(waiter: Waiter) -> None:
    schedule = Schedule()
    schedule.add_shift(Shift(waiter, MONDAY, time(18), time(23)))
    payroll = Payroll(schedule)
    assert payroll.night_bonus(waiter, MONDAY) == Decimal("2.00")
    assert payroll.gross_pay(waiter, MONDAY) == Decimal("52.00")
