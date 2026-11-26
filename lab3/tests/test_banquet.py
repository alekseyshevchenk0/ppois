from datetime import timedelta
from decimal import Decimal

import pytest

from restaurant.exceptions import InvalidDataError, ReservationConflictError, TableUnavailableError
from restaurant.guests.customer import Customer
from restaurant.hall.banquet import Banquet
from restaurant.hall.hall import Hall
from restaurant.hall.reservation_book import ReservationBook
from tests.constants import EVENING

PRICE = Decimal(50)


def make_banquet(organizer: Customer, hall: Hall, guests_count: int) -> Banquet:
    return Banquet(organizer, hall, EVENING, guests_count, PRICE)


def test_banquet_validation(adult_guest: Customer, main_hall: Hall) -> None:
    with pytest.raises(InvalidDataError):
        make_banquet(adult_guest, main_hall, 0)
    with pytest.raises(InvalidDataError):
        Banquet(adult_guest, main_hall, EVENING, 10, Decimal(0))


def test_required_tables_are_the_biggest_ones(adult_guest: Customer, main_hall: Hall, book: ReservationBook) -> None:
    tables = make_banquet(adult_guest, main_hall, 10).required_tables(book)
    assert [table.capacity for table in tables] == [8, 4]


def test_not_enough_tables(adult_guest: Customer, main_hall: Hall, book: ReservationBook) -> None:
    with pytest.raises(TableUnavailableError, match="Основной"):
        make_banquet(adult_guest, main_hall, 20).required_tables(book)


def test_confirm_books_all_tables_once(adult_guest: Customer, main_hall: Hall, book: ReservationBook) -> None:
    banquet = make_banquet(adult_guest, main_hall, 10)
    reservations = banquet.confirm(book)
    assert [reservation.guests_count for reservation in reservations] == [8, 2]
    assert banquet.is_confirmed()
    with pytest.raises(InvalidDataError):
        banquet.confirm(book)


def test_confirmed_banquet_blocks_the_hall(adult_guest: Customer, minor_guest: Customer, main_hall: Hall, book: ReservationBook) -> None:
    make_banquet(adult_guest, main_hall, 10).confirm(book)
    big_table = main_hall.find_table(4)
    with pytest.raises(ReservationConflictError):
        book.book(minor_guest, big_table, EVENING + timedelta(hours=1), 2)


def test_cancel_releases_tables(adult_guest: Customer, main_hall: Hall, book: ReservationBook) -> None:
    banquet = make_banquet(adult_guest, main_hall, 10)
    banquet.confirm(book)
    banquet.cancel()
    assert not banquet.is_confirmed()
    assert len(book.free_tables(main_hall, EVENING, 240, 1)) == 4


def test_unconfirmed_banquet_is_not_confirmed(adult_guest: Customer, main_hall: Hall) -> None:
    assert not make_banquet(adult_guest, main_hall, 10).is_confirmed()


def test_price_and_deposit(adult_guest: Customer, main_hall: Hall) -> None:
    banquet = make_banquet(adult_guest, main_hall, 10)
    assert banquet.total_price() == Decimal("500.00")
    assert banquet.deposit_amount() == Decimal("150.00")


def test_large_banquet_gets_a_discount(adult_guest: Customer, main_hall: Hall) -> None:
    assert make_banquet(adult_guest, main_hall, 30).total_price() == Decimal("1425.00")
