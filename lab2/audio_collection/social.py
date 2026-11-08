from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .constants import MAX_RATING, MIN_RATING, POSITIVE_RATING, SUMMARY_ELLIPSIS
from .exceptions import InvalidAmountError, InvalidRatingError


@dataclass(eq=False)
class Rating:
    track_title: str
    collector: str
    score: int

    def validate(self) -> None:
        if not MIN_RATING <= self.score <= MAX_RATING:
            raise InvalidRatingError("Оценка вне диапазона")

    def is_positive(self) -> bool:
        return self.score >= POSITIVE_RATING


@dataclass(eq=False)
class Review:
    author: str
    album_title: str
    text: str
    score: int

    def validate(self) -> None:
        if not MIN_RATING <= self.score <= MAX_RATING:
            raise InvalidRatingError("Оценка вне диапазона")
        if not self.text.strip():
            raise InvalidAmountError("Текст рецензии пуст")

    def summary(self, max_length: int) -> str:
        if len(self.text) <= max_length:
            return self.text
        return self.text[:max_length].rstrip() + SUMMARY_ELLIPSIS


@dataclass(eq=False)
class Favorites:
    owner: str
    track_titles: List[str] = field(default_factory=list)

    def add_track(self, title: str) -> bool:
        if title in self.track_titles:
            return False
        self.track_titles.append(title)
        return True


@dataclass(eq=False)
class Wishlist:
    owner: str
    budget: float
    album_titles: List[str] = field(default_factory=list)

    def fits_budget(self, prices: Dict[str, float]) -> bool:
        total = sum(prices.get(title, 0.0) for title in self.album_titles)
        return total <= self.budget
