from __future__ import annotations

from datetime import date
from restaurant.exceptions import InvalidDataError
from restaurant.guests.profile import GuestProfile
from restaurant.menu.dish import Dish
from restaurant.person import Person

REGULAR_VISITS = 5


class Customer(Person):
    def __init__(self, name: str, phone: str, birth_date: date, email: str, profile: GuestProfile | None = None) -> None:
        super().__init__(name, phone, birth_date)
        if "@" not in email:
            raise InvalidDataError(f"Адрес электронной почты «{email}» некорректен")
        self.email = email
        self.profile = profile or GuestProfile()
        self.visits_count = 0

    def register_visit(self) -> None:
        self.visits_count += 1

    def is_regular(self) -> bool:
        return self.visits_count >= REGULAR_VISITS

    def can_eat(self, dish: Dish) -> bool:
        return self.profile.accepts(dish)
