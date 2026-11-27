from random import Random
from typing import Callable, List, Optional, TypeVar

T = TypeVar("T")
K = TypeVar("K")
KeyFunc = Optional[Callable[[T], object]]


def _value(item: T, key: KeyFunc) -> object:
    return key(item) if key is not None else item


def merge_sort(
    items: List[T],
    key: KeyFunc = None,
    reverse: bool = False,
) -> List[T]:
    if not isinstance(items, list):
        raise TypeError("Ожидается список Python.")

    def merge(left: List[T], right: List[T]) -> List[T]:
        merged = []
        left_index = 0
        right_index = 0

        while left_index < len(left) and right_index < len(right):
            left_value = _value(left[left_index], key)
            right_value = _value(right[right_index], key)
            if (not left_value < right_value) if reverse else (
                not right_value < left_value
            ):
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1

        merged.extend(left[left_index:])
        merged.extend(right[right_index:])
        return merged

    def sort_part(part: List[T]) -> List[T]:
        if len(part) < 2:
            return part
        middle = len(part) // 2
        left_part = sort_part(part[:middle])
        right_part = sort_part(part[middle:])
        return merge(left_part, right_part)

    items[:] = sort_part(items)
    return items


def bozo_sort(
    items: List[T],
    key: KeyFunc = None,
    reverse: bool = False,
    max_attempts: int = 100_000,
    rng: Optional[Random] = None,
) -> List[T]:
    if not isinstance(items, list):
        raise TypeError("Ожидается список Python.")
    if max_attempts < 0:
        raise ValueError("Количество попыток не может быть отрицательным.")

    generator = rng if rng is not None else Random()

    def is_sorted() -> bool:
        for index in range(len(items) - 1):
            first = _value(items[index], key)
            second = _value(items[index + 1], key)
            if (first < second) if reverse else (second < first):
                return False
        return True

    attempts = 0
    while not is_sorted():
        if attempts >= max_attempts:
            raise TimeoutError(
                "Bozo sort превысил допустимое количество перестановок."
            )
        first_index = generator.randrange(len(items))
        second_index = generator.randrange(len(items))
        items[first_index], items[second_index] = (
            items[second_index],
            items[first_index],
        )
        attempts += 1
    return items
