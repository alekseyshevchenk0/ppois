from datetime import timedelta

from restaurant.guests.customer import Customer
from restaurant.hall.hall import Hall
from restaurant.hall.reservation_book import ReservationBook
from restaurant.hall.seating_planner import SeatingPlanner
from restaurant.hall.table import Table
from restaurant.hall.waitlist import Waitlist
from tests.constants import EVENING, NOW


def test_best_table_has_the_fewest_empty_seats(planner: SeatingPlanner, small_table: Table, medium_table: Table) -> None:
    assert planner.best_table(EVENING, 2) is small_table
    assert planner.best_table(EVENING, 4) is medium_table


def test_window_preference_can_change_the_choice(planner: SeatingPlanner, small_table: Table, window_table: Table) -> None:
    assert planner.best_table(EVENING, 2) is small_table
    assert planner.best_table(EVENING, 2, prefer_window=True) is window_table


def test_no_table_for_too_many_guests(planner: SeatingPlanner) -> None:
    assert planner.best_table(EVENING, 9) is None


def test_seat_books_the_best_table(planner: SeatingPlanner, book: ReservationBook, adult_guest: Customer, small_table: Table) -> None:
    reservation = planner.seat_or_wait(adult_guest, 2, EVENING, NOW)
    assert reservation is not None
    assert reservation.table is small_table
    assert book.reservations_of(adult_guest) == [reservation]


def test_guest_goes_to_waitlist_when_no_table(
    book: ReservationBook, waitlist: Waitlist, small_table: Table, adult_guest: Customer, minor_guest: Customer
) -> None:
    hall = Hall("Мини")
    hall.add_table(small_table)
    planner = SeatingPlanner([hall], book, waitlist)
    assert planner.seat_or_wait(adult_guest, 2, EVENING, NOW) is not None
    assert planner.seat_or_wait(minor_guest, 2, EVENING, NOW) is None
    assert waitlist.position_of(minor_guest) == 1


def test_waitlisted_guest_gets_the_freed_table(
    book: ReservationBook, waitlist: Waitlist, small_table: Table, adult_guest: Customer, minor_guest: Customer
) -> None:
    hall = Hall("Мини")
    hall.add_table(small_table)
    planner = SeatingPlanner([hall], book, waitlist)
    first = planner.seat_or_wait(adult_guest, 2, EVENING, NOW)
    planner.seat_or_wait(minor_guest, 2, EVENING, NOW)
    assert planner.promote_from_waitlist(small_table, EVENING) is None
    book.cancel(first)
    promoted = planner.promote_from_waitlist(small_table, EVENING)
    assert promoted is not None
    assert promoted.guest is minor_guest
    assert len(waitlist) == 0


def test_promote_with_empty_waitlist(planner: SeatingPlanner, small_table: Table) -> None:
    assert planner.promote_from_waitlist(small_table, EVENING) is None


def test_alternative_times_skip_busy_slots(
    book: ReservationBook, waitlist: Waitlist, small_table: Table, adult_guest: Customer
) -> None:
    hall = Hall("Мини")
    hall.add_table(small_table)
    planner = SeatingPlanner([hall], book, waitlist)
    planner.seat_or_wait(adult_guest, 2, EVENING, NOW)
    expected = [EVENING + timedelta(hours=2), EVENING + timedelta(hours=2, minutes=30), EVENING + timedelta(hours=3)]
    assert planner.suggest_alternative_times(2, EVENING) == expected


def test_alternative_times_can_be_empty(planner: SeatingPlanner) -> None:
    assert planner.suggest_alternative_times(20, EVENING) == []
