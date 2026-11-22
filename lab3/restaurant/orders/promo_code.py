from __future__ import annotations

from datetime import date

from restaurant.exceptions import InvalidDataError, InvalidPromoCodeError
from restaurant.orders.discount import Discount
from restaurant.validation import require_non_empty, require_positive


class PromoCode:
    def __init__(self, code: str, discount: Discount, valid_from: date, valid_until: date, max_uses: int) -> None:
        require_non_empty(code, "promo code")
        require_positive(max_uses, "max uses")
        if valid_until < valid_from:
            raise InvalidDataError("Промокод не может заканчиваться раньше, чем начинается")
        self.code = code
        self.discount = discount
        self.valid_from = valid_from
        self.valid_until = valid_until
        self.max_uses = max_uses
        self.uses = 0

    def is_valid_on(self, day: date) -> bool:
        return self.valid_from <= day <= self.valid_until

    def remaining_uses(self) -> int:
        return self.max_uses - self.uses

    def redeem(self, day: date) -> Discount:
        if not self.is_valid_on(day):
            raise InvalidPromoCodeError(self.code, "срок действия не подходит")
        if self.remaining_uses() == 0:
            raise InvalidPromoCodeError(self.code, "лимит использований исчерпан")
        self.uses += 1
        return self.discount
