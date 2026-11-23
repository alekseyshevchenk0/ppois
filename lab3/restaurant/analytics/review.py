from __future__ import annotations

from datetime import date
from enum import Enum

from restaurant.exceptions import InvalidDataError
from restaurant.guests.customer import Customer
from restaurant.menu.dish import Dish


class ReviewStatus(Enum):
    PENDING = "на проверке"
    APPROVED = "одобрен"
    REJECTED = "отклонён"


class Review:
    def __init__(self, customer: Customer, dish: Dish, rating: int, comment: str, created_on: date) -> None:
        if not 1 <= rating <= 5:
            raise InvalidDataError("Оценка должна быть от 1 до 5")
        self.customer = customer
        self.dish = dish
        self.rating = rating
        self.comment = comment.strip()
        self.created_on = created_on
        self.status = ReviewStatus.PENDING

    def approve(self) -> None:
        self._ensure_pending()
        self.status = ReviewStatus.APPROVED

    def reject(self) -> None:
        self._ensure_pending()
        self.status = ReviewStatus.REJECTED

    def is_visible(self) -> bool:
        return self.status is ReviewStatus.APPROVED

    def _ensure_pending(self) -> None:
        if self.status is not ReviewStatus.PENDING:
            raise InvalidDataError("Отзыв уже обработан")
