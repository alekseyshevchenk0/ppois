from __future__ import annotations

from datetime import date

from restaurant.validation import require_non_empty

ADULT_AGE = 18


class Person:

    def __init__(self, name: str, phone: str, birth_date: date) -> None:
        require_non_empty(name, "person name")
        require_non_empty(phone, "person phone")
        self.name = name
        self.phone = phone
        self.birth_date = birth_date

    def age_on(self, today: date) -> int:
        years = today.year - self.birth_date.year
        had_birthday = (today.month, today.day) >= (self.birth_date.month, self.birth_date.day)
        return years if had_birthday else years - 1

    def is_adult(self, today: date) -> bool:
        return self.age_on(today) >= ADULT_AGE

    def matches(self, query: str) -> bool:
        return query.strip().lower() in self.name.lower()
