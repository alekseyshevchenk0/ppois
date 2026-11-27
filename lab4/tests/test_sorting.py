import pytest
from random import Random

from models import Student
from sorting import bozo_sort, merge_sort


def test_merge_sort_numbers():
    values = [5, 1, 4, 2, 3]
    result = merge_sort(values)
    assert result == [1, 2, 3, 4, 5]
    assert result is values


def test_merge_sort_empty_and_single():
    assert merge_sort([]) == []
    assert merge_sort([1]) == [1]


def test_merge_sort_reverse_and_key():
    assert merge_sort([1, 5, 2, 4], reverse=True) == [5, 4, 2, 1]
    students = [Student("A", 2), Student("B", 5), Student("C", 3)]
    assert [item.grade for item in merge_sort(students, key=lambda x: x.grade)] == [
        2, 3, 5
    ]


def test_merge_sort_stability():
    values = [("a", 2), ("b", 1), ("c", 2)]
    assert merge_sort(values, key=lambda item: item[1]) == [
        ("b", 1), ("a", 2), ("c", 2)
    ]


def test_merge_sort_rejects_non_list():
    with pytest.raises(TypeError):
        merge_sort((3, 2, 1))


def test_bozo_sort_already_sorted():
    values = [1, 2, 3]
    assert bozo_sort(values) == values


def test_bozo_sort_reorders_with_seed():
    values = [3, 1, 2]
    assert bozo_sort(values, rng=Random(4)) == [1, 2, 3]


def test_bozo_sort_reverse_and_key():
    values = [1, 3, 2]
    assert bozo_sort(values, reverse=True, rng=Random(2)) == [3, 2, 1]
    students = [Student("A", 2), Student("B", 1)]
    bozo_sort(students, key=lambda item: item.grade, rng=Random(3))
    assert [item.grade for item in students] == [1, 2]


def test_bozo_sort_errors():
    with pytest.raises(TypeError):
        bozo_sort("321")
    with pytest.raises(ValueError):
        bozo_sort([2, 1], max_attempts=-1)
    with pytest.raises(TimeoutError):
        bozo_sort([2, 1], max_attempts=0)


def test_bozo_sort_empty():
    assert bozo_sort([]) == []
