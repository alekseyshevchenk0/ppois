import pytest

from restaurant.exceptions import InvalidDataError, TableUnavailableError
from restaurant.hall.hall import Hall
from restaurant.hall.table import Table


def test_table_validation() -> None:
    with pytest.raises(InvalidDataError):
        Table(0, 4)
    with pytest.raises(InvalidDataError):
        Table(1, 0)


def test_table_fits_and_wasted_seats(medium_table: Table) -> None:
    assert medium_table.fits(4)
    assert not medium_table.fits(5)
    assert medium_table.wasted_seats(3) == 1
    with pytest.raises(TableUnavailableError, match="Стол №3"):
        medium_table.wasted_seats(5)


def test_table_service_flag(medium_table: Table) -> None:
    medium_table.take_out_of_service()
    assert not medium_table.is_in_service
    medium_table.return_to_service()
    assert medium_table.is_in_service


def test_hall_name_required() -> None:
    with pytest.raises(InvalidDataError):
        Hall(" ")


def test_hall_add_find_remove(main_hall: Hall, medium_table: Table) -> None:
    assert [table.number for table in main_hall.tables] == [1, 2, 3, 4]
    with pytest.raises(InvalidDataError):
        main_hall.add_table(Table(3, 6))
    assert main_hall.find_table(3) is medium_table
    assert main_hall.remove_table(3) is medium_table
    assert main_hall.find_table(3) is None
    with pytest.raises(InvalidDataError):
        main_hall.remove_table(3)


def test_hall_capacity_ignores_tables_out_of_service(main_hall: Hall, big_table: Table) -> None:
    assert main_hall.total_capacity() == 17
    big_table.take_out_of_service()
    assert main_hall.total_capacity() == 9


def test_hall_tables_for_and_window(main_hall: Hall, window_table: Table, big_table: Table) -> None:
    assert [table.number for table in main_hall.tables_for(4)] == [3, 4]
    big_table.take_out_of_service()
    assert [table.number for table in main_hall.tables_for(4)] == [3]
    assert main_hall.window_tables() == [window_table]
