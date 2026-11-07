from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from .constants import EMAIL_PATTERN, MIN_PASSWORD_LENGTH
from .exceptions import InvalidTrackDataError, WeakPasswordError

if TYPE_CHECKING:
    from .commerce import Subscription


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@dataclass(eq=False)
class Artist:
    name: str
    birth_year: int = 0
    genres: List[str] = field(default_factory=list)

    def age(self, current_year: int) -> int:
        if current_year < self.birth_year:
            raise InvalidTrackDataError("Год раньше года рождения")
        return current_year - self.birth_year


@dataclass(eq=False)
class Band(Artist):
    members: List[Artist] = field(default_factory=list)
    formed_year: int = 0

    def add_member(self, member: Artist) -> None:
        if any(existing is member for existing in self.members):
            raise InvalidTrackDataError("Участник уже в группе")
        self.members.append(member)


@dataclass(eq=False)
class Composer:
    name: str
    country: str


@dataclass(eq=False)
class Collector:
    username: str
    email: str
    joined_year: int
    password_hash: str = ""
    subscription: Optional[Subscription] = None

    def has_valid_email(self) -> bool:
        return re.fullmatch(EMAIL_PATTERN, self.email) is not None

    def set_password(self, password: str) -> None:
        has_digit = any(char.isdigit() for char in password)
        if len(password) < MIN_PASSWORD_LENGTH or not has_digit:
            raise WeakPasswordError("Пароль слишком слабый")
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return hash_password(password) == self.password_hash

    def has_active_subscription(self, today: int) -> bool:
        return self.subscription is not None and self.subscription.is_active(today)
