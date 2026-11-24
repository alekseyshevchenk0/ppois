from __future__ import annotations

from datetime import date
from decimal import Decimal

from restaurant.exceptions import InvalidDataError
from restaurant.guests.loyalty import LoyaltyCard
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
        self.loyalty_card: LoyaltyCard | None = None

    def register_visit(self) -> None:
        self.visits_count += 1

    def is_regular(self) -> bool:
        return self.visits_count >= REGULAR_VISITS

    def attach_card(self, card: LoyaltyCard) -> None:
        if self.loyalty_card is not None:
            raise InvalidDataError(f"У гостя «{self.name}» уже есть карта лояльности")
        self.loyalty_card = card

    def can_eat(self, dish: Dish) -> bool:
        return self.profile.accepts(dish)

    def discount_percent(self) -> Decimal:
        return self.loyalty_card.discount_percent() if self.loyalty_card else Decimal(0)

    def earn_loyalty_points(self, amount_spent: Decimal) -> int:
        return self.loyalty_card.earn_points(amount_spent) if self.loyalty_card else 0
