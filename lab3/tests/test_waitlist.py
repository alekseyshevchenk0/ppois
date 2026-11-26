from datetime import timedelta

import pytest

from restaurant.exceptions import InvalidDataError
from restaurant.guests.customer import Customer
from restaurant.hall.table import Table
from restaurant.hall.waitlist import Waitlist
from tests.constants import NOW


def test_join_and_duplicate(waitlist: Waitlist, adult_guest: Customer) -> None:
    waitlist.join(adult_guest, 2, NOW)
    assert len(waitlist) == 1
    with pytest.raises(InvalidDataError):
        waitlist.join(adult_guest, 2, NOW)
    with pytest.raises(InvalidDataError):
        waitlist.join(Customer("Ivan", "1", adult_guest.birth_date, "i@example.com"), 0, NOW)


def test_leave(waitlist: Waitlist, adult_guest: Customer, minor_guest: Customer) -> None:
    waitlist.join(adult_guest, 2, NOW)
    waitlist.leave(adult_guest)
    assert len(waitlist) == 0
    with pytest.raises(InvalidDataError):
        waitlist.leave(minor_guest)


def test_waitlist_is_first_come_first_served(waitlist: Waitlist, adult_guest: Customer, minor_guest: Customer) -> None:
    waitlist.join(adult_guest, 2, NOW)
    waitlist.join(minor_guest, 2, NOW + timedelta(minutes=10))
    assert waitlist.position_of(adult_guest) == 1
    assert waitlist.position_of(minor_guest) == 2


def test_same_priority_is_first_come_first_served(waitlist: Waitlist, adult_guest: Customer, minor_guest: Customer) -> None:
    waitlist.join(minor_guest, 2, NOW + timedelta(minutes=5))
    waitlist.join(adult_guest, 2, NOW)
    assert [entry.guest for entry in waitlist.ordered()] == [adult_guest, minor_guest]


def test_estimated_wait(waitlist: Waitlist, adult_guest: Customer, minor_guest: Customer, gold_guest: Customer) -> None:
    for offset, guest in enumerate((adult_guest, minor_guest, gold_guest)):
        waitlist.join(guest, 2, NOW + timedelta(minutes=offset))
    assert waitlist.estimated_wait_minutes(adult_guest, tables_count=2, turnover_minutes=60) == 60
    assert waitlist.estimated_wait_minutes(gold_guest, tables_count=2, turnover_minutes=60) == 120
    with pytest.raises(InvalidDataError):
        waitlist.estimated_wait_minutes(minor_guest, tables_count=0, turnover_minutes=60)


def test_next_for_skips_groups_that_do_not_fit(
    waitlist: Waitlist, adult_guest: Customer, minor_guest: Customer, small_table: Table
) -> None:
    waitlist.join(adult_guest, 4, NOW)
    waitlist.join(minor_guest, 2, NOW + timedelta(minutes=5))
    assert waitlist.next_for(small_table).guest is minor_guest
    assert waitlist.take_next_for(small_table).guest is minor_guest
    assert waitlist.take_next_for(small_table) is None
    assert len(waitlist) == 1


def test_entry_waited_minutes(waitlist: Waitlist, adult_guest: Customer) -> None:
    entry = waitlist.join(adult_guest, 2, NOW)
    assert entry.waited_minutes(NOW + timedelta(minutes=25)) == 25
