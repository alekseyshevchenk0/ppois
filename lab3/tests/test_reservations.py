from datetime import datetime, timedelta

import pytest

from restaurant.exceptions import ReservationConflictError, TableUnavailableError
from restaurant.guests.customer import Customer
from restaurant.hall.hall import Hall
from restaurant.hall.reservation import NO_SHOW_GRACE_MINUTES, Reservation
from restaurant.hall.reservation_book import ReservationBook
from restaurant.hall.table import Table
from tests.constants import EVENING


def test_reservation_validation(adult_guest: Customer, small_table: Table) -> None:
    with pytest.raises(TableUnavailableError):
        Reservation(adult_guest, small_table, EVENING, 3)


def test_reservation_end_and_overlap(adult_guest: Customer, medium_table: Table) -> None:
    reservation = Reservation(adult_guest, medium_table, EVENING, 2, duration_minutes=90)
    assert reservation.end_time() == EVENING + timedelta(minutes=90)
    assert reservation.overlaps_with(EVENING + timedelta(minutes=60), EVENING + timedelta(minutes=120))
    assert not reservation.overlaps_with(reservation.end_time(), reservation.end_time() + timedelta(hours=1))


def test_no_show_detection(adult_guest: Customer, medium_table: Table) -> None:
    reservation = Reservation(adult_guest, medium_table, EVENING, 2)
    on_time = EVENING + timedelta(minutes=NO_SHOW_GRACE_MINUTES)
    assert not reservation.is_no_show(on_time)
    assert reservation.is_no_show(on_time + timedelta(minutes=1))
    reservation.mark_arrived()
    assert not reservation.is_no_show(on_time + timedelta(hours=1))


def test_cancelled_reservation_is_not_a_no_show(adult_guest: Customer, medium_table: Table) -> None:
    reservation = Reservation(adult_guest, medium_table, EVENING, 2)
    reservation.cancel()
    assert not reservation.is_active()
    assert not reservation.is_no_show(EVENING + timedelta(hours=2))


def test_book_and_conflict(book: ReservationBook, adult_guest: Customer, minor_guest: Customer, medium_table: Table) -> None:
    book.book(adult_guest, medium_table, EVENING, 2)
    with pytest.raises(ReservationConflictError, match="Стол №3"):
        book.book(minor_guest, medium_table, EVENING + timedelta(hours=1), 2)
    later = book.book(minor_guest, medium_table, EVENING + timedelta(hours=2), 2)
    assert later.start == EVENING + timedelta(hours=2)


def test_cancel_frees_the_table(book: ReservationBook, adult_guest: Customer, minor_guest: Customer, medium_table: Table) -> None:
    reservation = book.book(adult_guest, medium_table, EVENING, 2)
    book.cancel(reservation)
    assert book.is_table_free(medium_table, EVENING, 120)
    book.book(minor_guest, medium_table, EVENING, 2)


def test_table_out_of_service_cannot_be_booked(book: ReservationBook, adult_guest: Customer, medium_table: Table) -> None:
    medium_table.take_out_of_service()
    assert not book.is_table_free(medium_table, EVENING, 120)
    with pytest.raises(TableUnavailableError, match="выведен"):
        book.book(adult_guest, medium_table, EVENING, 2)


def test_reservation_queries(book: ReservationBook, adult_guest: Customer, minor_guest: Customer, medium_table: Table, big_table: Table) -> None:
    first = book.book(adult_guest, medium_table, EVENING, 2)
    second = book.book(minor_guest, big_table, EVENING + timedelta(days=1), 2)
    assert book.reservations_of(adult_guest) == [first]
    assert book.reservations_on(EVENING.date()) == [first]
    assert book.reservations_on(second.start.date()) == [second]


def test_free_tables(book: ReservationBook, main_hall: Hall, adult_guest: Customer, medium_table: Table) -> None:
    book.book(adult_guest, medium_table, EVENING, 2)
    free = book.free_tables(main_hall, EVENING, 120, 2)
    assert [table.number for table in free] == [1, 2, 4]


def test_release_no_shows(book: ReservationBook, adult_guest: Customer, minor_guest: Customer, medium_table: Table, big_table: Table) -> None:
    missed = book.book(adult_guest, medium_table, EVENING, 2)
    arrived = book.book(minor_guest, big_table, EVENING, 2)
    arrived.mark_arrived()
    now = datetime(2026, 11, 21, 19, 30)
    assert book.no_shows(now) == [missed]
    assert book.release_no_shows(now) == 1
    assert book.is_table_free(medium_table, EVENING, 120)
