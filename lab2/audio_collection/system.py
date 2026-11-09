from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .constants import (
    CLIPPING_LEVEL,
    DEFAULT_THEME,
    DEFAULT_VOLUME,
    INFO_LEVEL,
    MAX_VOLUME,
    MIN_VOLUME,
    URGENT_LEVEL,
    VALID_THEMES,
)
from .exceptions import InvalidAmountError, InvalidVolumeError


@dataclass(eq=False)
class Settings:
    theme: str = DEFAULT_THEME
    default_volume: int = DEFAULT_VOLUME
    autoplay: bool = False

    def validate(self) -> None:
        if self.theme not in VALID_THEMES:
            raise InvalidAmountError("Неизвестная тема оформления")
        if not MIN_VOLUME <= self.default_volume <= MAX_VOLUME:
            raise InvalidVolumeError("Громкость по умолчанию вне диапазона")


@dataclass(eq=False)
class Notification:
    message: str
    created_day: int
    level: str = INFO_LEVEL
    read: bool = False

    def is_urgent(self) -> bool:
        return self.level == URGENT_LEVEL


@dataclass(eq=False)
class NotificationCenter:
    owner: str
    notifications: List[Notification] = field(default_factory=list)

    def notify(self, message: str, today: int, level: str = INFO_LEVEL) -> Notification:
        notification = Notification(message, today, level)
        self.notifications.append(notification)
        return notification

    def unread_count(self) -> int:
        return sum(1 for item in self.notifications if not item.read)


@dataclass(eq=False)
class LoudnessAnalyzer:
    samples: List[int] = field(default_factory=list)

    def peak(self) -> int:
        return max((abs(sample) for sample in self.samples), default=0)

    def has_clipping(self) -> bool:
        return self.peak() >= CLIPPING_LEVEL
