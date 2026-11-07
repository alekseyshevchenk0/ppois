from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .constants import (
    GENRE_PATH_SEPARATOR,
    HIGH_QUALITY_COVER_SIDE,
    REDACTION_MARK,
    SECONDS_PER_MINUTE,
)
from .exceptions import InvalidTrackDataError


@dataclass(frozen=True)
class Duration:

    total_seconds: int

    def __post_init__(self) -> None:
        if self.total_seconds < 0:
            raise InvalidTrackDataError("Длительность не может быть отрицательной")

    @classmethod
    def from_minutes_seconds(cls, minutes: int, seconds: int) -> Duration:
        return cls(minutes * SECONDS_PER_MINUTE + seconds)

    def format(self) -> str:
        minutes, seconds = divmod(self.total_seconds, SECONDS_PER_MINUTE)
        return f"{minutes:02d}:{seconds:02d}"


@dataclass(eq=False)
class Genre:
    name: str
    parent: Optional[Genre] = None

    def full_path(self) -> str:
        names = [self.name]
        node = self.parent
        while node is not None:
            names.append(node.name)
            node = node.parent
        return GENRE_PATH_SEPARATOR.join(reversed(names))


@dataclass(eq=False)
class Tag:
    name: str
    weight: int = 1


@dataclass(eq=False)
class Label:
    name: str
    founded_year: int

    def age(self, current_year: int) -> int:
        return current_year - self.founded_year


@dataclass(eq=False)
class CoverArt:
    image_path: str
    width: int
    height: int

    def is_high_quality(self) -> bool:
        return min(self.width, self.height) >= HIGH_QUALITY_COVER_SIDE


@dataclass(eq=False)
class Lyrics:
    text: str
    language: str

    def word_count(self) -> int:
        return len(self.text.split())

    def censored(self, banned_words: List[str]) -> str:
        result = self.text
        for word in banned_words:
            result = result.replace(word, REDACTION_MARK * len(word))
        return result
