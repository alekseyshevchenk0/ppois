from __future__ import annotations

import math
from datetime import date
from decimal import Decimal

from restaurant.exceptions import InvalidDataError
from restaurant.staff.employee import Employee
from restaurant.validation import require_non_empty

MIN_SKILL = 1
MAX_SKILL = 5
BASELINE_SKILL = 3
SPEED_STEP = 0.1


class Cook(Employee):

    role_title = "cook"

    def __init__(
        self, name: str, phone: str, birth_date: date, hourly_rate: Decimal, hire_date: date, station: str, skill_level: int = BASELINE_SKILL
    ) -> None:
        super().__init__(name, phone, birth_date, hourly_rate, hire_date)
        require_non_empty(station, "station")
        if not MIN_SKILL <= skill_level <= MAX_SKILL:
            raise InvalidDataError(f"Skill level must be between {MIN_SKILL} and {MAX_SKILL}")
        self.station = station
        self.skill_level = skill_level

    def can_work_station(self, station: str) -> bool:
        return self.station == station

    def move_to_station(self, station: str) -> None:
        require_non_empty(station, "station")
        self.station = station

    def promote(self) -> None:
        if self.skill_level == MAX_SKILL:
            raise InvalidDataError("Cook already has the maximum skill level")
        self.skill_level += 1

    def speed_factor(self) -> float:
        return 1 - (self.skill_level - BASELINE_SKILL) * SPEED_STEP

    def adjusted_minutes(self, base_minutes: int) -> int:
        return math.ceil(base_minutes * self.speed_factor())
