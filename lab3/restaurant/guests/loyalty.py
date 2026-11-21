from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum

from restaurant.exceptions import InsufficientPointsError
from restaurant.validation import require_non_empty, require_positive

POINTS_PER_CURRENCY_UNIT = Decimal("0.1")


class LoyaltyTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


TIER_THRESHOLDS = {LoyaltyTier.SILVER: 500, LoyaltyTier.GOLD: 2000}
TIER_DISCOUNT_PERCENT = {LoyaltyTier.BRONZE: Decimal(0), LoyaltyTier.SILVER: Decimal(5), LoyaltyTier.GOLD: Decimal(10)}


class LoyaltyCard:
    def __init__(self, number: str, issued_on: date) -> None:
        require_non_empty(number, "card number")
        self.number = number
        self.issued_on = issued_on
        self.balance = 0
        self.lifetime_points = 0

    def earn_points(self, amount_spent: Decimal) -> int:
        require_positive(amount_spent, "amount spent")
        points = int(amount_spent * POINTS_PER_CURRENCY_UNIT)
        self.balance += points
        self.lifetime_points += points
        return points

    def redeem_points(self, points: int) -> None:
        require_positive(points, "points to redeem")
        if points > self.balance:
            raise InsufficientPointsError(points, self.balance)
        self.balance -= points

    def tier(self) -> LoyaltyTier:
        for tier, threshold in sorted(TIER_THRESHOLDS.items(), key=lambda item: item[1], reverse=True):
            if self.lifetime_points >= threshold:
                return tier
        return LoyaltyTier.BRONZE

    def discount_percent(self) -> Decimal:
        return TIER_DISCOUNT_PERCENT[self.tier()]

    def points_to_next_tier(self) -> int:
        for threshold in sorted(TIER_THRESHOLDS.values()):
            if self.lifetime_points < threshold:
                return threshold - self.lifetime_points
        return 0
